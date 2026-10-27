#!/usr/bin/env python3
"""Package this workspace's skills as .skill files for Claude Cowork's "Save skill" card.

Usage (Cowork Bash sandbox, from the workspace root):
    python3 .claude/setup/cowork_skills.py package <out_dir> [--video] [--previous <old_workspace>]

Packages the core skills (plus every other skill with --video) into <out_dir>/<name>.skill,
one zip per skill with the skill folder at the zip root. Each skill is first checked against
Cowork's upload rules. What was packaged is recorded in .claude/cowork-skills.json.

With --previous (an update), the old workspace's record decides: only skills that are new,
changed or not packaged before get a .skill, its video choice carries over, and skills it
recorded that are no longer offered are listed as removed. An old workspace without a record
used loader skills: everything is packaged and "loaders: yes" is printed.
Prints one line per .skill file. Exits 1 if any skill fails the checks.
"""
import argparse
import fnmatch
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

CORE = (
    "personal-memory", "memory-setup", "meeting", "professional-guidance", "talk-it-through",
    "brainstorm-idea", "adhd", "teach", "handoff", "startday-spec", "workflow-builder",
    "antislop", "antislop-code", "antislop-copywriting", "antislop-human", "antislop-layoutmobile",
    "antislop-ui", "excalidraw-diagram", "youtube", "troubleshoot-my-pc",
)
# The workspace owner's maintenance skill; never installed for end users.
NEVER = ("convert-release",)
RECORD = Path(".claude") / "cowork-skills.json"

ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
SKIP_DIRS = {"__pycache__", "node_modules"}
SKIP_GLOBS = ("*.pyc", ".DS_Store")


def frontmatter(text):
    """Return ({key: value}, problems). Folded or multi-line values are joined.

    A small parser, not full YAML: it also reports the forms YAML would reject."""
    m = re.match(r"^---\n(.*?)\n---", text.replace("\r\n", "\n"), re.S)
    if not m:
        return None, ["no frontmatter"]
    keys, probs, current = {}, [], None
    for line in m.group(1).split("\n"):
        if line.startswith("\t"):
            probs.append("frontmatter uses a tab for indentation")
        km = re.match(r"^([A-Za-z0-9_-]+):(.*)$", line)
        if km:
            current, value = km.group(1), km.group(2)
            if value and not value.startswith(" "):
                probs.append(f"frontmatter '{current}:' needs a space after the colon")
            value = value.strip()
            if value[:1] not in ("'", '"') and ": " in value:
                probs.append(f"frontmatter '{current}' has an unquoted ': ' (quote the value)")
            keys[current] = "" if value in (">", "|", ">-", "|-") else value.strip("\"'")
        elif current and line.startswith((" ", "\t")):
            keys[current] = (keys[current] + " " + line.strip()).strip()
    return keys, probs


def skipped(rel):
    parts = rel.parts
    return (bool(SKIP_DIRS & set(parts)) or (len(parts) > 1 and parts[0] == "evals")
            or any(fnmatch.fnmatch(rel.name, g) for g in SKIP_GLOBS))


def skill_files(folder):
    return sorted(p for p in folder.rglob("*") if p.is_file() and not skipped(p.relative_to(folder)))


def fingerprint(folder):
    h = hashlib.sha256()
    for p in skill_files(folder):
        h.update(p.relative_to(folder).as_posix().encode() + b"\0")
        h.update(p.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    return h.hexdigest()


def check(folder):
    """Return a list of problems that would make Cowork reject this skill."""
    md = folder / "SKILL.md"
    if not md.is_file():
        return ["no SKILL.md"]
    probs = []
    extra_md = [p for p in skill_files(folder) if p.name == "SKILL.md" and p != md]
    if extra_md:
        probs.append(f"{len(extra_md)} extra SKILL.md file(s), e.g. {extra_md[0].relative_to(folder)}")
    fm, fm_probs = frontmatter(md.read_text(encoding="utf-8"))
    probs += fm_probs
    if fm is None:
        return probs
    if set(fm) - ALLOWED_KEYS:
        probs.append(f"frontmatter keys not allowed: {', '.join(sorted(set(fm) - ALLOWED_KEYS))}")
    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != folder.name:
        probs.append(f"name {name!r} does not match the folder")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        probs.append("name must be kebab-case, at most 64 characters")
    if not desc:
        probs.append("missing description")
    if "<" in desc or ">" in desc:
        probs.append("description contains < or >")
    if len(desc) > 1024:
        probs.append(f"description is {len(desc)} characters (max 1024)")
    return probs


def package(folder, out_dir):
    dest = out_dir / f"{folder.name}.skill"
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in skill_files(folder):
            z.write(p, Path(folder.name) / p.relative_to(folder))
    return dest


def offered(skills_dir, video):
    names = sorted(p.name for p in skills_dir.iterdir() if (p / "SKILL.md").is_file())
    return [n for n in names if n not in NEVER and (video or n in CORE)]


def read_record(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {"video": bool(data.get("video")), "skills": dict(data.get("skills", {}))}
    except (OSError, ValueError, AttributeError):
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=["package"])
    ap.add_argument("out_dir")
    ap.add_argument("--video", action="store_true", help="also package every non-core skill")
    ap.add_argument("--previous", help="the workspace this one replaces (an update)")
    ap.add_argument("--workspace", default=".", help="workspace root (default: current folder)")
    args = ap.parse_args(argv)

    ws = Path(args.workspace).resolve()
    skills_dir = ws / ".claude" / "skills"
    if not skills_dir.is_dir():
        print(f"{skills_dir} not found; run from the workspace root", file=sys.stderr)
        return 2
    missing = [n for n in CORE if not (skills_dir / n / "SKILL.md").is_file()]
    if missing:
        print(f"note: core skills not in this workspace: {', '.join(missing)}")

    video, before = args.video, {}
    if args.previous:
        prev = Path(args.previous).resolve()
        if prev == ws or not (prev / ".claude").is_dir():
            print(f"--previous must be the old workspace folder, not this one: {prev}", file=sys.stderr)
            return 2
        old = read_record(prev / RECORD)
        if old is None:
            print("loaders: yes (the previous workspace used loader skills; every skill is packaged)")
        else:
            video = video or old["video"]
            before = old["skills"]
    names = offered(skills_dir, video)
    for gone in sorted(set(before) - set(names)):
        print(f"removed: {gone}")

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    record = {"video": video, "skills": {n: h for n, h in before.items() if n in names}}
    failed = packaged = 0
    for n in names:
        fp = fingerprint(skills_dir / n)
        if before.get(n) == fp:
            continue
        probs = check(skills_dir / n)
        if probs:
            failed += 1
            print(f"FAILED {n}: {'; '.join(probs)}")
            record["skills"].pop(n, None)
            continue
        dest = package(skills_dir / n, out_dir)
        record["skills"][n] = fp
        packaged += 1
        print(f"{dest} ({dest.stat().st_size // 1024} KB)")
    if not packaged and not failed:
        print("nothing to install: no new or changed skills")
    (ws / RECORD).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
