#!/usr/bin/env python3
"""Ready-made Claude Cowork skill packages (.skill files) for this workspace.

Maintainer, once per Release (after convert-release):
    python3 .claude/cowork/cowork_skills.py build
Checks every skill in .claude/skills/ against Cowork's upload rules and writes
.claude/cowork/skills/core/<name>.skill, .claude/cowork/skills/video/<name>.skill and
.claude/cowork/skills/index.json. Builds are byte-identical when a skill is unchanged.
Exits 1 if any skill fails the checks (it is left out).

Owner's agent, on an update only:
    python3 .claude/cowork/cowork_skills.py changed <old_workspace> [--video]
Lists the ready-made .skill files to show: skills that are new, changed, or newly offered
compared with <old_workspace>, plus "removed: <name>" and "moved to video: <name>" lines.
An old workspace without an index lists every offered skill; if it used loader skills it
also prints "loaders: yes".
Nothing is built on the owner's side.
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
# The workspace maintainer's own skill; never packaged.
NEVER = ("convert-release",)
PACKAGES = Path(".claude") / "cowork" / "skills"
INDEX = PACKAGES / "index.json"
ZIP_DATE = (1980, 1, 1, 0, 0, 0)

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
    """Packaged files, in the same order on every platform (Windows paths sort case-blind)."""
    files = [p for p in folder.rglob("*") if p.is_file() and not skipped(p.relative_to(folder))]
    return sorted(files, key=lambda p: p.relative_to(folder).as_posix())


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


def file_bytes(p):
    data = p.read_bytes()
    return data if b"\0" in data[:8192] else data.replace(b"\r\n", b"\n")


def fingerprint(folder):
    """Hash of the skill's packaged content; independent of platform and zlib version."""
    h = hashlib.sha256()
    for p in skill_files(folder):
        h.update(p.relative_to(folder).as_posix().encode() + b"\0" + file_bytes(p) + b"\0")
    return h.hexdigest()


def package(folder, dest):
    """Zip the skill with its folder at the zip root. Same input, same bytes (on one platform)."""
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in skill_files(folder):
            data = file_bytes(p)
            info = zipfile.ZipInfo((Path(folder.name) / p.relative_to(folder)).as_posix(), ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100755 if data.startswith(b"#!") else 0o100644) << 16
            z.writestr(info, data)


def build(ws):
    skills_dir, out = ws / ".claude" / "skills", ws / PACKAGES
    names = sorted(p.name for p in skills_dir.iterdir() if (p / "SKILL.md").is_file() and p.name not in NEVER)
    missing = [n for n in CORE if n not in names]
    if missing:
        print(f"note: core skills not in this workspace: {', '.join(missing)}")
    index, failed = {}, 0
    for kind in ("core", "video"):
        (out / kind).mkdir(parents=True, exist_ok=True)
    for n in names:
        kind = "core" if n in CORE else "video"
        probs = check(skills_dir / n)
        if probs:
            failed += 1
            print(f"FAILED {n}: {'; '.join(probs)}")
            continue
        dest = out / kind / f"{n}.skill"
        package(skills_dir / n, dest)
        index[n] = {"set": kind, "sha256": fingerprint(skills_dir / n)}
    for stale in sorted(out.glob("*/*.skill")):
        if index.get(stale.stem, {}).get("set") != stale.parent.name:
            stale.unlink()
            print(f"deleted stale {stale.relative_to(ws).as_posix()}")
    (ws / INDEX).write_text(json.dumps(index, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    sizes = {k: sum(p.stat().st_size for p in (out / k).glob("*.skill")) // 1024 for k in ("core", "video")}
    print(f"built {len(index)} skills: core {sizes['core']} KB, video {sizes['video']} KB")
    return 1 if failed else 0


def changed(ws, prev, video):
    if prev == ws or not (prev / ".claude").is_dir():
        print(f"the argument must be the old workspace folder, not this one: {prev}", file=sys.stderr)
        return 2
    new = json.loads((ws / INDEX).read_text(encoding="utf-8"))
    try:
        old = json.loads((prev / INDEX).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        old = None
        # A short-lived edition packaged skills itself and kept .claude/cowork-skills.json; no loaders.
        if not (prev / ".claude" / "cowork-skills.json").is_file():
            print("loaders: yes (the old workspace used loader skills; show every listed file)")
    offer = {n: e for n, e in new.items() if video or e["set"] == "core"}
    shown = 0
    if old is not None:
        had = {n for n, e in old.items() if video or e["set"] == "core"}
        for gone in sorted(had - set(offer)):
            print(f"moved to video: {gone}" if gone in new else f"removed: {gone}")
    for n, e in sorted(offer.items()):
        before = (old or {}).get(n)
        if old is not None and before and before["sha256"] == e["sha256"] and (video or before["set"] == "core"):
            continue
        print((PACKAGES / e["set"] / f"{n}.skill").as_posix())
        shown += 1
    if not shown:
        print("nothing to install: no new or changed skills")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="maintainer: rebuild the .skill packages and index")
    b.add_argument("--workspace", default=".")
    c = sub.add_parser("changed", help="update: list the packages to show")
    c.add_argument("old_workspace")
    c.add_argument("--video", action="store_true", help="the owner has the video skills")
    c.add_argument("--workspace", default=".")
    args = ap.parse_args(argv)
    ws = Path(args.workspace).resolve()
    if not (ws / ".claude" / "skills").is_dir():
        print(f"{ws} has no .claude/skills; run from the workspace root", file=sys.stderr)
        return 2
    if args.command == "build":
        return build(ws)
    return changed(ws, Path(args.old_workspace).resolve(), args.video)


if __name__ == "__main__":
    sys.exit(main())
