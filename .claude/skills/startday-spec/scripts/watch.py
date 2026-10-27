#!/usr/bin/env python3
"""Report what changed in watched files, folders and web pages. Read-only on targets.

    python3 .claude/skills/startday-spec/scripts/watch.py [--config .claude/startday.json] [--state .claude/startday.state.json]
    python3 .claude/skills/startday-spec/scripts/watch.py --ack      # after every reported change was handled

Config: {"watch": [{"path": "~/Meetings", "use": "meetings", "why": "..."}, {"url": "https://...", "why": "..."}]}.
Prints a JSON list of changes and exits 0; exits 1 on a missing or bad config.

- The first sighting of a target is a baseline: recorded, nothing reported.
- A reported change stays pending, and is printed again every run, until `--ack`. A run that dies before
  handling its changes loses nothing.
- A file modified in the last SETTLE seconds is skipped until a later run, so a transcript still being
  written is never reported half done.
- Each file change carries `id`, the first 8 hex of sha256 of the file's path: stable across edits, so a
  transcript that is fixed or extended later maps to the same meeting.
- Pages are compared as visible text (scripts and styles dropped), so markup churn is not a change.
- A target that cannot be read reports `error` (never pending) and keeps its old baseline.
"""
import argparse
import difflib
import hashlib
import html.parser
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

SETTLE = 120
MAX_TEXT = 200_000
DIFF_LINES = 40
TIMEOUT = 30


class _Text(html.parser.HTMLParser):
    SKIP = {"script", "style", "noscript", "template"}

    def __init__(self):
        super().__init__()
        self.out, self.depth = [], 0

    def handle_starttag(self, tag, attrs):
        self.depth += tag in self.SKIP

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if not self.depth and data.strip():
            self.out.append(" ".join(data.split()))


def page_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "startday-watch"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        raw = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
    p = _Text()
    p.feed(raw)
    return "\n".join(p.out)[:MAX_TEXT]


def files_under(root):
    if root.is_file():
        return [root]
    # ponytail: rehashes every file each run; fine for a transcripts folder, add an mtime/size cache for big trees
    return sorted(p for p in root.rglob("*")
                  if p.is_file() and not any(part.startswith(".") for part in p.relative_to(root).parts))


def load_config(path):
    try:
        targets = json.loads(Path(path).read_text(encoding="utf-8"))["watch"]
    except FileNotFoundError:
        raise SystemExit(f"watch config not found: {path}")
    except (ValueError, KeyError, TypeError) as e:
        raise SystemExit(f"watch config {path} needs a top-level \"watch\" list: {e!r}")
    if not isinstance(targets, list):
        raise SystemExit(f"watch config {path}: \"watch\" must be a list")
    for t in targets:
        if not isinstance(t, dict) or ("path" in t) == ("url" in t):
            raise SystemExit(f"watch config {path}: each entry needs exactly one of \"path\" or \"url\": {t!r}")
    return targets


def check_path(t, state, now, out):
    root = Path(os.path.expanduser(t["path"])).resolve()
    key = f"path:{root}"
    base = {"target": t["path"], "use": t.get("use"), "why": t.get("why")}
    if not root.exists():
        out.append({**base, "change": "error", "detail": f"not found: {root}"})
        return
    known = state["files"].get(key)
    seen = {}
    for p in files_under(root):
        try:
            if now - p.stat().st_mtime < SETTLE:
                if known is not None and str(p) in known:
                    seen[str(p)] = known[str(p)]  # still being written: keep the old hash, report later
                continue
            h = hashlib.sha256(p.read_bytes()).hexdigest()
        except OSError:
            continue
        seen[str(p)] = h
        if known is not None and known.get(str(p)) != h:
            out.append({**base, "change": "changed" if str(p) in known else "new", "file": str(p), "sha256": h,
                        "id": path_id(p)})
    if known is not None:
        for p in sorted(set(known) - set(seen)):
            if not Path(p).exists():
                out.append({**base, "change": "gone", "file": p, "id": path_id(p)})
            else:
                seen[p] = known[p]  # unreadable this run: keep its baseline
    state["files"][key] = seen


def check_url(t, state, out):
    url = t["url"]
    base = {"target": url, "use": t.get("use"), "why": t.get("why")}
    try:
        text = page_text(url)
    except Exception as e:  # any fetch or decode failure keeps the old baseline
        out.append({**base, "change": "error", "detail": repr(e)})
        return
    old = state["pages"].get(url)
    if old is not None and old != text:
        diff = list(difflib.unified_diff(old.splitlines(), text.splitlines(), lineterm="", n=1))[2:]
        out.append({**base, "change": "changed", "diff": diff[:DIFF_LINES]})
    state["pages"][url] = text


def path_id(p):
    return hashlib.sha256(str(p).encode()).hexdigest()[:8]


def merge(pending, change):
    """One pending entry per file or page. A file still `new` to the agent stays `new` when it changes again;
    a page keeps its first diff line set plus the newest."""
    key = change.get("file") or change["target"]
    old = pending.get(key)
    if old and old["change"] == "new" and change["change"] == "changed":
        change = {**change, "change": "new"}
    if old and "diff" in old and "diff" in change:
        change = {**change, "diff": (old["diff"] + ["..."] + change["diff"])[-DIFF_LINES:]}
    pending[key] = change


def main(argv=None):
    ap = argparse.ArgumentParser(prog="watch.py")
    ap.add_argument("--config", default=".claude/startday.json")
    ap.add_argument("--state", default=".claude/startday.state.json")
    ap.add_argument("--ack", action="store_true", help="clear the pending changes (after handling them)")
    a = ap.parse_args(argv)
    try:
        state = json.loads(Path(a.state).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = {}
    for k in ("files", "pages", "pending"):
        state.setdefault(k, {})
    out = []
    if a.ack:
        print(f"acked {len(state['pending'])}")
        state["pending"] = {}
    else:
        try:
            targets = load_config(a.config)
        except SystemExit as e:
            print(e, file=sys.stderr)
            return 1
        now = time.time()
        for t in targets:
            found = []
            try:
                check_path(t, state, now, found) if "path" in t else check_url(t, state, found)
            except Exception as e:  # one bad target (permissions, dropped share) never blocks the rest
                found.append({"target": t.get("path") or t.get("url"), "use": t.get("use"), "why": t.get("why"),
                              "change": "error", "detail": repr(e)})
            for c in found:
                out.append(c) if c["change"] == "error" else merge(state["pending"], c)
    tmp = Path(a.state).with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(tmp, a.state)
    if not a.ack:
        print(json.dumps(list(state["pending"].values()) + out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
