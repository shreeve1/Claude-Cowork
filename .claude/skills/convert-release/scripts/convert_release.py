#!/usr/bin/env python3
"""Convert an upstream Release (Codex layout: AGENTS.md, .agents/) into this workspace's
Claude Cowork layout (CLAUDE.md, .claude/).

Usage (from the workspace root, in the Cowork Bash sandbox):
    python3 .claude/skills/convert-release/scripts/convert_release.py <release_dir> <out_dir>

Writes a converted copy to <out_dir> (must not exist) with a fresh MANIFEST.json whose
sha256 values match the converted files, so the converted copy can be verified
exactly as upstream verifies the original. The original Release is never modified.
Only mechanical, repeatable rules live here. Cowork-specific rules are not shipped files:
they live in memory (`memory/preferences/cowork-environment.md`).
"""
import hashlib
import json
import sys
from pathlib import Path

# Codex-only files dropped from the converted Release.
DROP_SUFFIXES = ("/agents/openai.yaml",)

TEXT_EXT = (".md", ".py", ".json", ".txt", ".html", ".toml", ".yaml", ".ps1", ".sh", ".gitignore")

# Files where AGENTS.md is a real web standard, not this workspace's instructions file.
KEEP_AGENTS_MD = (".claude/skills/workflow-builder/agents-library/",)

TEXT_RULES = [
    (".agents/skills", ".claude/skills"),
    (".agents\\skills", ".claude\\skills"),
    (".agents/", ".claude/"),
    (".agents\\", ".claude\\"),
    ('".agents"', '".claude"'),
    ("(`.agents`, `.githooks`)", "(`.claude`, `.githooks`)"),
    ("Call the `read` tool on", "Call `Read` on"),
    ("Never use the `question` tool", "Never use the `AskUserQuestion` tool"),
    ("No `question` tool", "No `AskUserQuestion` tool"),
    ("use `question` when", "use `AskUserQuestion` when"),
    ("use `question` with", "use `AskUserQuestion` with"),
    ("Use `read`, `glob`, `grep`, and limited `bash`", "Use `Read`, `Glob`, `Grep`, and limited `Bash`"),
    ("Use `task` subagents", "Use `Agent` subagents"),
    ("use `task` subagents", "use `Agent` subagents"),
    ("Use `webfetch`", "Use `web_fetch`"),
    ("Use `read` for directories when possible. Use `bash`",
     "Use `Glob` (or `ls` via Bash) for directories. Use `Bash`"),
    ("Use `glob` and `grep`", "Use `Glob` and `Grep`"),
    ("then `read` the `memory/preferences/` directory",
     "then list the `memory/preferences/` directory (Glob `memory/preferences/*.md`)"),
]

# Per-file rules, applied after TEXT_RULES and the AGENTS.md rename. None are needed now.
FILE_RULES = {}


def new_path(rel):
    if rel == "AGENTS.md":
        return "CLAUDE.md"
    if rel.startswith(".agents/"):
        return ".claude/" + rel[len(".agents/"):]
    return rel


def is_text(rel, data):
    if b"\0" in data[:8192]:
        return False
    name = rel.rsplit("/", 1)[-1]
    return rel.endswith(TEXT_EXT) or "." not in name or rel.startswith(".githooks/")


def convert_text(rel, text):
    for a, b in TEXT_RULES:
        text = text.replace(a, b)
    if not rel.startswith(KEEP_AGENTS_MD):
        text = text.replace("AGENTS.md", "CLAUDE.md")
    for a, b in FILE_RULES.get(rel, []):
        if a not in text:
            raise SystemExit(f"{rel}: rule no longer matches upstream text: {a!r}; update convert_release.py")
        text = text.replace(a, b)
    return text


def sha(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    src, out = Path(argv[0]).resolve(), Path(argv[1]).resolve()
    mpath = src / "MANIFEST.json"
    if not mpath.is_file():
        print(f"{src} has no MANIFEST.json", file=sys.stderr)
        return 2
    if out.exists():
        print(f"{out} already exists; pick a new folder", file=sys.stderr)
        return 2
    man = json.loads(mpath.read_text(encoding="utf-8"))
    files = {}
    for rel, meta in man["files"].items():
        if rel.endswith(DROP_SUFFIXES):
            continue
        data = (src / rel).read_bytes()
        nrel = new_path(rel)
        if is_text(nrel, data):
            data = convert_text(nrel, data.decode("utf-8")).encode("utf-8")
        dest = out / nrel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        mode = meta.get("mode")
        if mode:
            dest.chmod(int(mode, 8))
        files[nrel] = dict(meta, sha256=sha(data))
    man["files"] = dict(sorted(files.items()))
    (out / "MANIFEST.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    print(f"converted {len(files)} files -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
