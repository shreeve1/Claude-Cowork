#!/usr/bin/env python3
"""Deterministic audit for personal memory.

Checks that memory/index.md is in sync with the promoted topic files, that the
topic-ized folders (workflows, decisions) hold only topic subfolders plus a
generated index, that the two sub-indexes are current (`indexes.py` drift), and
that Client Memory under memory/<client_folder>/ (default clients) is well formed and listed on its hub.
memory/candidates/ is not audited. When memory/rules.md exists, every skill and
path a row names must exist, and every preference/email file must be reachable
from it (named in a row, or in a memory file a row names).
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hubs  # noqa: E402
import indexes  # noqa: E402
import links  # noqa: E402
import schema  # noqa: E402

PROMOTED_DIRS = ["preferences", "docs", "voice", "email", "guides"]
CROWDED_LIMIT = 15
CLIENT_KEYS = ["type", "client", "subject", "title", "verified", "source"]
RULE_SKILL = re.compile(r"skill `([^`]+)`")
TICK = re.compile(r"`([^`]+)`")
RULE_REACHED_DIRS = ["preferences", "email"]
SIZE_LIMIT = 6144
SUMMARY_LIMIT = 160
STALE_DAYS = 90
SCAFFOLD = {"README.md", "TEMPLATES.md", "index.md"}
HISTORY_LINE = re.compile(
    r"(?im)^\s*-?\s*(?:superseded|amended|updated)\s+\d{4}-\d{2}-\d{2}\b"
    r"|^\s*-?\s*\d{4}-\d{2}-\d{2}:?\s+(?:superseded|amended)\b"
    r"|^\s*-\s*\d{4}-\d{2}-\d{2}:")
CHANGED_LINE = re.compile(r"(?im)^\s*-?\s*changed\s+\d{4}-\d{2}-\d{2}")
TABLE_PADDING = re.compile(r"[^|\s] {2,}\|")
SEPARATOR_ROW = re.compile(r"\|[\s:|-]+\|")


def indexed_paths(memory_dir):
    """Paths linked from memory/index.md plus the two sub-indexes."""
    content = hubs.read_note(memory_dir / "index.md")
    backticks = re.findall(r"`(memory/[^`]+)`", content)
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
    paths = {path for _, path in links} | set(backticks)
    topic_dirs = schema.load(memory_dir)["topic_dirs"]
    for d in topic_dirs:
        idx = memory_dir / d / "index.md"
        if idx.exists():
            text = hubs.read_note(idx)
            paths |= {p for _, p in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)}
    return paths


def audit_index(memory_dir, indexed):
    actual_files = []
    for d in PROMOTED_DIRS:
        p_dir = memory_dir / d
        if p_dir.exists():
            actual_files.extend(f"memory/{d}/{f.name}" for f in sorted(p_dir.glob("*.md")))
    missing = [f for f in actual_files if f not in indexed]
    stale = sorted(
        p for p in indexed
        if p.startswith("memory/") and not (memory_dir / p[len("memory/"):]).exists()
    )
    return missing, stale


def audit_topic_dirs(memory_dir, indexed):
    """Problems in workflows/decisions: flat promoted files, unknown topics, drift."""
    data = schema.load(memory_dir)
    topic_dirs = data["topic_dirs"]
    topics = data["topics"]
    problems = []
    for d in topic_dirs:
        base = memory_dir / d
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.is_file():
                if child.name not in ("index.md", ".gitkeep"):
                    problems.append(
                        f"memory/{d}/{child.name}: promoted file directly in {d}/ (move it into a topic folder)")
            elif child.is_dir() and child.name not in topics:
                problems.append(f"memory/{d}/{child.name}: topic folder not in {topics}")
        for topic in topics:
            tdir = base / topic
            if tdir.is_dir():
                for p in sorted(tdir.glob("*.md")):
                    rel = "memory/" + p.relative_to(memory_dir).as_posix()
                    if rel not in indexed:
                        problems.append(f"{rel}: missing from memory/{d}/index.md")
    changed, _ = indexes.drift(memory_dir)
    problems.extend(f"index drift: {p} (run indexes.py)" for p in changed)
    return problems


def audit_index_links(memory_dir):
    """memory/index.md must link each sub-index."""
    content = hubs.read_note(memory_dir / "index.md")
    topic_dirs = schema.load(memory_dir)["topic_dirs"]
    return [f"memory/index.md: missing link to memory/{d}/index.md"
            for d in topic_dirs if f"memory/{d}/index.md" not in content]


def rule_rows(memory_dir):
    """Body rows of the memory/rules.md table (header and separator dropped)."""
    text = hubs.read_note(memory_dir / "rules.md")
    rows = [l for l in text.splitlines() if l.startswith("|")]
    return [r for r in rows if not re.fullmatch(r"\|[\s:|-]+\|", r)
            and r.split("|")[1].strip() != "When"]


def audit_rules(memory_dir):
    """Broken pointers in memory/rules.md and preference/email files no rule reaches."""
    if not (memory_dir / "rules.md").exists():
        return []
    root = memory_dir.resolve().parent
    skills, paths = set(), set()
    for row in rule_rows(memory_dir):
        skills |= set(RULE_SKILL.findall(row))
        paths |= {t for t in TICK.findall(row)
                  if ("/" in t or t.endswith(".md")) and not any(c in t for c in "<*")}
    problems = [f"memory/rules.md: skill {s} not found" for s in sorted(skills)
                if not (root / ".claude" / "skills" / s / "SKILL.md").exists()]
    problems += [f"memory/rules.md: {p} not found" for p in sorted(paths) if not (root / p).exists()]
    reached = set(paths)
    for p in paths:
        if p.startswith("memory/") and p.endswith(".md") and (root / p).exists():
            reached |= set(re.findall(r"memory/[\w./-]+\.md", hubs.read_note(root / p)))
    for d in RULE_REACHED_DIRS:
        for f in sorted((memory_dir / d).glob("*.md")):
            rel = f"memory/{d}/{f.name}"
            if rel not in reached:
                problems.append(f"{rel}: no row in memory/rules.md reaches it")
    return problems


def crowded(memory_dir):
    """'crowded: memory/<dir> <n> files' lines for any non-topic memory folder
    holding more than CROWDED_LIMIT .md files directly (excluding index.md)."""
    topic_dirs = schema.load(memory_dir)["topic_dirs"]
    out = []
    for d in sorted(p for p in memory_dir.iterdir() if p.is_dir()):
        if d.name in topic_dirs:
            continue
        n = len([f for f in d.glob("*.md") if f.name != "index.md"])
        if n > CROWDED_LIMIT:
            out.append(f"crowded: memory/{d.name} {n} files")
    return out


def note_files(memory_dir):
    """Hand-written memory notes: generated indexes, hubs, scaffold and raw/candidates excluded."""
    return sorted(p for p in memory_dir.rglob("*.md")
                  if p.name not in SCAFFOLD and not {"_hubs", "raw", "candidates"} & set(p.parts))


def compact_row(row):
    """One index table row without alignment padding; rows already compact come back unchanged."""
    if SEPARATOR_ROW.fullmatch(row):
        if " " not in row:
            return row
        cells = [re.sub(r"-+", "---", re.sub(r"\s+", "", c)) for c in row.strip("|").split("|")]
        return "|" + "|".join(cells) + "|"
    if row.startswith("|") and TABLE_PADDING.search(row):
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", row.strip())[1:-1]]
        return "| " + " | ".join(cells) + " |"
    return row


def compact_index(text):
    """memory/index.md text with table padding removed. Read at every session start, so padding is paid every time."""
    out = []
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        out.append(compact_row(body) + line[len(body):])
    return "".join(out)


def bloat(memory_dir):
    """Warning lines for oversize notes, long summaries, history lines, retired files and the retired log."""
    out = []
    if (memory_dir / "log.md").exists():
        out.append("memory/log.md is retired: put the entry in the commit message and delete the file")
    if not (memory_dir / "rules.md").exists() and any(any((memory_dir / d).glob("*.md")) for d in RULE_REACHED_DIRS):
        out.append("memory/rules.md is missing: preference and email files are not routed")
    for p in note_files(memory_dir):
        if p.name == "log.md" and p.parent == memory_dir:
            continue
        rel = "memory/" + p.relative_to(memory_dir).as_posix()
        try:
            p.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            out.append(f"{rel}: not UTF-8")
        text = hubs.read_note(p).split("\n---\n", 1)[-1]
        fm = hubs.parse_frontmatter(p)
        if p.stat().st_size > SIZE_LIMIT:
            out.append(f"{rel}: {p.stat().st_size} bytes, over {SIZE_LIMIT}; trim or split")
        if len(fm.get("summary", "")) > SUMMARY_LIMIT:
            out.append(f"{rel}: summary {len(fm['summary'])} chars, over {SUMMARY_LIMIT}")
        if fm.get("status") == "superseded":
            out.append(f"{rel}: status superseded; delete the file, git keeps it")
        elif HISTORY_LINE.search(text):
            out.append(f"{rel}: history line; overwrite in place, git keeps the old text")
        elif len(CHANGED_LINE.findall(text)) > 1:
            out.append(f"{rel}: more than one Changed line; keep only the reason that still matters")
    for row in hubs.read_note(memory_dir / "index.md").splitlines():
        cells = row.split("|")
        if row.startswith("| [") and len(cells) > 3 and len(cells[3].strip()) > SUMMARY_LIMIT:
            out.append(f"memory/index.md: row {cells[1].strip()} summary over {SUMMARY_LIMIT} chars")
    index_text = hubs.read_note(memory_dir / "index.md")
    saved = len(index_text.encode("utf-8")) - len(compact_index(index_text).encode("utf-8"))
    if saved:
        out.append(f"memory/index.md: table padding costs {saved} bytes every session; run gate.py compact")
    return out


def note_date(path):
    """Newest valid `updated`/`verified` frontmatter date, or None."""
    fm = hubs.parse_frontmatter(path)
    days = []
    for key in ("updated", "verified"):
        try:
            days.append(date.fromisoformat(fm.get(key, "")[:10]))
        except ValueError:
            pass
    return max(days, default=None)


def stale_notes(memory_dir, today=None):
    """(date, path) for notes whose newest updated/verified date is older than STALE_DAYS, oldest first."""
    today = today or date.today()
    found = []
    for p in note_files(memory_dir):
        day = note_date(p)
        if day and (today - day).days > STALE_DAYS:
            found.append((day.isoformat(), "memory/" + p.relative_to(memory_dir).as_posix()))
    return sorted(found)


def audit_clients(memory_dir, indexed):
    data = schema.load(memory_dir)
    folder = data["client_folder"]
    root = memory_dir / folder
    subjects = data["client_subjects"]
    problems = []
    known = set(PROMOTED_DIRS) | set(data["topic_dirs"]) | {"candidates", "raw", folder}
    for d in sorted(p for p in memory_dir.iterdir() if p.is_dir() and p.name not in known):
        stray = next((n for n in sorted(d.rglob("*.md")) if hubs.parse_frontmatter(n).get("type") == "client-memory"), None)
        if stray:
            problems.append(f"memory/{d.name}/: holds Client Memory notes (e.g. {stray.name}) but client_folder is "
                            f"'{folder}'; set client_folder to '{d.name}' in memory/schema.json or move the notes")
    for p in hubs.note_paths(memory_dir):
        rel = "memory/" + p.relative_to(memory_dir).as_posix()
        parts = p.relative_to(root).parts
        if len(parts) != 3:
            problems.append(f"{rel}: not at {folder}/<subject>/<short>/<slug>.md")
            continue
        subject, short, _ = parts
        fm = hubs.parse_frontmatter(p)
        missing = [k for k in CLIENT_KEYS if not fm.get(k)]
        if missing:
            problems.append(f"{rel}: missing frontmatter {missing}")
        if subject not in subjects:
            problems.append(f"{rel}: folder subject '{subject}' not in {subjects}")
        if fm.get("subject") and fm["subject"] not in subjects:
            problems.append(f"{rel}: subject '{fm['subject']}' not in {subjects}")
        if fm.get("subject") and fm["subject"] != subject:
            problems.append(f"{rel}: frontmatter subject '{fm['subject']}' != folder '{subject}'")
        if fm.get("client") and fm["client"] != short:
            problems.append(f"{rel}: frontmatter client '{fm['client']}' != folder '{short}'")
        if fm.get("type") and fm["type"] != "client-memory":
            problems.append(f"{rel}: type '{fm['type']}' != 'client-memory'")
        hub = root / hubs.HUB_DIR / f"{short}.md"
        if not hub.exists() or f"]({rel})" not in hubs.read_note(hub):
            problems.append(f"{rel}: not listed on hub memory/{folder}/{hubs.HUB_DIR}/{short}.md")
    changed, stale = hubs.drift(memory_dir)
    problems.extend(f"hub out of date: {p} (run hubs.py)" for p in changed)
    problems.extend(f"hub stale: {p} (run hubs.py)" for p in stale)
    hub_dir = root / hubs.HUB_DIR
    if hub_dir.is_dir():
        for h in sorted(hub_dir.glob("*.md")):
            rel = "memory/" + h.relative_to(memory_dir).as_posix()
            if rel not in indexed:
                problems.append(f"{rel}: hub has no memory/index.md row")
    return problems


def main():
    ap = argparse.ArgumentParser(description="Audit personal memory index and Client Memory.")
    ap.add_argument("--memory", default="memory", help="Memory directory root (default: memory)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("audit", help="Audit index alignment and Client Memory")
    sub.add_parser("crowded", help="Report memory folders holding more than 15 direct .md files")
    sub.add_parser("stale", help=f"List notes not updated or verified in over {STALE_DAYS} days")
    sub.add_parser("compact", help="Rewrite memory/index.md without table padding")
    sub.add_parser("links", help="Report broken links and notes with no outgoing or inbound links")
    bl = sub.add_parser("backlinks", help="List notes linking to a note")
    bl.add_argument("path", help="Note path in memory/<rel> form")

    args = ap.parse_args()
    mem_path = Path(args.memory)

    if args.cmd == "crowded":
        for line in crowded(mem_path):
            print(line)
        sys.exit(0)
    if args.cmd == "stale":
        for day, rel in stale_notes(mem_path):
            print(f"{day} {rel}")
        sys.exit(0)
    if args.cmd == "compact":
        path = mem_path / "index.md"
        if not path.exists():
            print("Alert: The memory index file (memory/index.md) was not found.")
            sys.exit(1)
        with open(path, encoding="utf-8", newline="") as f:
            old = f.read()
        new = compact_index(old)
        if new != old:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new)
        print(f"memory/index.md: {len(old.encode('utf-8')) - len(new.encode('utf-8'))} bytes removed")
        sys.exit(0)
    if args.cmd == "links":
        graph = links.build(mem_path)
        brk = links.broken(graph, mem_path)
        if brk:
            print("Broken links:")
            for src, target in brk:
                print(f"- {src} -> {target}")
        out = links.no_outgoing(graph)
        if out:
            print("No outgoing links:")
            for p in out:
                print(f"- {p}")
        inc = links.no_inbound(graph)
        if inc:
            print("No inbound links:")
            for p in inc:
                print(f"- {p}")
        print(f"links: {len(links.notes(graph))} notes, {len(brk)} broken, {len(out)} no outgoing, {len(inc)} no inbound")
        sys.exit(0)
    if args.cmd == "backlinks":
        found = links.backlinks(links.build(mem_path), args.path)
        if found:
            for src in found:
                print(f"- {src}")
        else:
            print("none")
        sys.exit(0)


    if args.cmd != "audit":
        ap.error(f"unknown command: {args.cmd}")

    if not (mem_path / "index.md").exists():
        print("Alert: The memory index file (memory/index.md) was not found.")
        sys.exit(1)
    indexed = indexed_paths(mem_path)
    missing, stale = audit_index(mem_path, indexed)
    topic_problems = audit_topic_dirs(mem_path, indexed)
    index_link_problems = audit_index_links(mem_path)
    client_problems = audit_clients(mem_path, indexed)
    rule_problems = audit_rules(mem_path)
    failed = False
    if missing or stale:
        print("Memory index out of sync: missing_from_index=%s stale_in_index=%s" % (missing, stale))
        failed = True
    if topic_problems:
        print("Topic folder problems:")
        for line in topic_problems:
            print(f"- {line}")
        failed = True
    if index_link_problems:
        print("Memory index structure problems:")
        for line in index_link_problems:
            print(f"- {line}")
        failed = True
    if client_problems:
        print("Client Memory problems:")
        for line in client_problems:
            print(f"- {line}")
        failed = True
    if rule_problems:
        print("Rules problems:")
        for line in rule_problems:
            print(f"- {line}")
        failed = True
    graph = links.build(mem_path)
    warnings = crowded(mem_path) + bloat(mem_path)
    warnings.extend(f"{src}: broken link {target}" for src, target in links.broken(graph, mem_path))
    for line in warnings:
        print(f"Warning: {line}")
    if failed:
        sys.exit(1)
    print("Success: Memory index and Client Memory are in sync.")
    sys.exit(0)


if __name__ == "__main__":
    main()