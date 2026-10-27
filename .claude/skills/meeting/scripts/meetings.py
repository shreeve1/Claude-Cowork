#!/usr/bin/env python3
"""List, show and archive the meeting transcripts waiting in one folder, for the `meeting` skill.

    python3 .claude/skills/meeting/scripts/meetings.py --folder <transcripts folder> list
    python3 .claude/skills/meeting/scripts/meetings.py --folder <transcripts folder> show <key>
    python3 .claude/skills/meeting/scripts/meetings.py --folder <transcripts folder> archive <key>

A meeting is one transcript file (.txt .md .vtt .srt .json .docx) or one subfolder holding such files, for
tools that save a folder per meeting. Names starting with "." and the archive folder (default
`<folder>/Archive`) are skipped. Only `archive` writes: it moves one meeting into the archive folder.
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import html
import io
import json
import os
import re
import shutil
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXTENSIONS = {".txt", ".md", ".vtt", ".srt", ".json", ".docx"}
# A transcription tool may still be writing a file changed this recently.
SETTLE_SECONDS = 120
# Meeting Records sit in a `meetings/` folder one or two levels down: notes/meetings/, clients/<short>/meetings/.
RECORD_GLOBS = ("*/meetings/*.md", "*/*/meetings/*.md")


def slug(name: str) -> str:
    return re.sub(r"[\W_]+", "-", name.lower()).strip("-")[:60] or "meeting"


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def cue_text(raw: str) -> str:
    """WebVTT or SRT as plain lines, each prefixed with its cue's start time; cue numbers and timings dropped."""
    out, start, in_note = [], None, False
    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if in_note:
            in_note = bool(line)
            continue
        if line == "NOTE" or line.startswith(("NOTE ", "STYLE", "REGION")):
            in_note = True  # a WebVTT comment or header block runs to the next blank line
            continue
        if "-->" in line:
            start = line.split("-->")[0].strip().replace(",", ".").split(".")[0]
            continue
        if not line or line.isdigit() or line == "WEBVTT" or line.startswith("WEBVTT "):
            continue
        spoken = re.sub(r"<v(?:\.[^ >]+)?\s+([^>]+)>", r"\1: ", line)
        spoken = re.sub(r"<[^>]+>", "", spoken).strip()
        if spoken:
            out.append(f"{start} {spoken}" if start else spoken)
    return "\n".join(out)


def json_lines(node: object) -> list[str]:
    """Every `text` value in document order, with its speaker when one sits beside it.

    A node whose children hold text yields only the children, so a full-text field next to its segments
    (Whisper and similar tools) is not read twice.
    """
    if isinstance(node, list):
        return [line for item in node for line in json_lines(item)]
    if not isinstance(node, dict):
        return []
    inner = [line for key, value in node.items() if key != "text" for line in json_lines(value)]
    text = node.get("text")
    if inner or not isinstance(text, str) or not text.strip():
        return inner
    who = next((node[k] for k in ("speaker", "speaker_name", "name") if isinstance(node.get(k), str)), None)
    return [f"{who}: {text.strip()}" if who else text.strip()]


def docx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
    except (zipfile.BadZipFile, KeyError):
        return ""
    xml = xml.replace("<w:tab/>", " ").replace("<w:br/>", "\n")
    paragraphs = (html.unescape(re.sub(r"<[^>]+>", "", p)).strip() for p in xml.split("</w:p>"))
    return "\n".join(p for p in paragraphs if p)


def read_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".docx":
        return docx_text(path)
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    if ext in (".vtt", ".srt"):
        return cue_text(raw)
    if ext == ".json":
        try:
            return "\n".join(json_lines(json.loads(raw)))
        except ValueError:
            return raw.strip()
    return raw.strip()


def transcript_files(entry: Path) -> list[Path]:
    if entry.is_file():
        return [entry] if entry.suffix.lower() in EXTENSIONS else []
    return sorted(p for p in entry.rglob("*")
                  if p.is_file() and p.suffix.lower() in EXTENSIONS
                  and not any(part.startswith(".") for part in p.relative_to(entry).parts))


def transcript(entry: Path) -> str:
    """The meeting's readable text; a folder's files each under a `## <file>` heading."""
    files = transcript_files(entry)
    if entry.is_file():
        return read_text(entry) if files else ""
    parts = ((f, read_text(f)) for f in files)
    return "\n\n".join(f"## {f.relative_to(entry).as_posix()}\n\n{text}" for f, text in parts if text)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def newest_mtime(entry: Path) -> float:
    if entry.is_file():
        return entry.stat().st_mtime
    return max([entry.stat().st_mtime] + [p.stat().st_mtime for p in entry.rglob("*")])


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    out = {}
    for line in text.splitlines()[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if sep:
            out[key.strip()] = value.split(" #")[0].strip().strip("\"'")
    return out


def record_index(root: Path) -> tuple[dict[str, str], dict[str, str]]:
    """({transcript_hash: record}, {source name: record}) for every Meeting Record in the workspace."""
    by_hash: dict[str, str] = {}
    by_name: dict[str, str] = {}
    for pattern in RECORD_GLOBS:
        for p in sorted(root.glob(pattern)):
            fm = frontmatter(p.read_text(encoding="utf-8", errors="replace")[:4000])
            if fm.get("type") != "meeting-record":
                continue
            if fm.get("transcript_hash"):
                by_hash.setdefault(fm["transcript_hash"], rel(p, root))
            if fm.get("source"):
                by_name.setdefault(fm["source"], rel(p, root))
    return by_hash, by_name


def scan(folder: Path, archive_dir: Path, root: Path, now: float | None = None) -> list[dict]:
    """Every meeting waiting in `folder`, newest first."""
    now = time.time() if now is None else now
    by_hash, by_name = record_index(root)
    items, keys = [], set()
    for entry in sorted(folder.iterdir()):
        if entry.name.startswith(".") or entry.resolve() == archive_dir.resolve() or not transcript_files(entry):
            continue
        text = transcript(entry)
        h = digest(text)
        key = base = slug(entry.stem if entry.is_file() else entry.name)
        n = 2
        while key in keys:
            key, n = f"{base}-{n}", n + 1
        keys.add(key)
        mtime = newest_mtime(entry)
        same_text, same_name = by_hash.get(h), by_name.get(entry.name)
        # Done only when one record has both this text and this name. Same name, new text: the transcript
        # changed. Same text, other name: a copy or a re-export; the skill asks before skipping it.
        record = same_name if same_name and same_name == same_text else None
        items.append({
            "key": key, "name": entry.name, "path": rel(entry, root), "kind": "file" if entry.is_file() else "folder",
            "modified": datetime.fromtimestamp(mtime).astimezone().isoformat(timespec="minutes"),
            "words": len(text.split()), "transcript_hash": h, "settling": mtime > now - SETTLE_SECONDS,
            "record": record, "same_name_record": None if record else same_name,
            "same_text_record": None if record else same_text, "_mtime": mtime,
        })
    items.sort(key=lambda i: i["_mtime"], reverse=True)
    return items


def public(item: dict) -> dict:
    return {k: v for k, v in item.items() if not k.startswith("_")}


def find(items: list[dict], key: str, folder: Path) -> dict:
    """One meeting by key, name, or any path inside it (startday hands over changed file paths)."""
    if "/" in key or os.sep in key:
        try:
            key = Path(key).expanduser().resolve().relative_to(folder.resolve()).parts[0]
        except (ValueError, IndexError):
            raise SystemExit(f"{key} is not inside {folder}") from None
    hits = [i for i in items if key in (i["key"], i["name"])]
    if len(hits) != 1:
        raise SystemExit(f"{len(hits)} meetings match {key!r}; run `list` for keys")
    return hits[0]


def free_name(folder: Path, name: str, is_file: bool) -> Path:
    """`name` in `folder`, or `name (2)`, `name (3)`... when taken; never an existing path."""
    stem, suffix = (Path(name).stem, Path(name).suffix) if is_file else (name, "")
    candidate, n = folder / name, 2
    while candidate.exists() or candidate.with_name(candidate.name + ".partial").exists():
        candidate, n = folder / f"{stem} ({n}){suffix}", n + 1
    return candidate


def file_hashes(path: Path) -> dict[str, str]:
    """{name inside the meeting: sha256}; a single file is keyed "." so a copy under another name compares equal."""
    if path.is_file():
        return {".": hashlib.sha256(path.read_bytes()).hexdigest()}
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob("*")) if p.is_file()}


def remove(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def move_no_overwrite(src: Path, dest: Path) -> None:
    """Rename `src` to `dest`, failing with FileExistsError if `dest` appeared meanwhile.

    POSIX rename replaces an existing file, so a file is hard-linked first (link refuses an existing name) and
    the old name unlinked. Windows rename already refuses an existing name. A folder rename onto an existing
    non-empty folder fails everywhere.
    """
    if os.name == "nt" or src.is_dir():
        if dest.exists():
            raise FileExistsError(errno.EEXIST, "exists", str(dest))
        os.rename(src, dest)
        return
    try:
        os.link(src, dest)
    except OSError as e:
        if e.errno not in (errno.EPERM, errno.ENOTSUP, errno.EOPNOTSUPP):
            raise
        if dest.exists():  # this filesystem has no hard links: best effort
            raise FileExistsError(errno.EEXIST, "exists", str(dest)) from e
        os.rename(src, dest)
        return
    os.unlink(src)


def copy_then_remove(src: Path, dest: Path) -> None:
    """Move across drives: copy to `<dest>.partial`, compare every file, rename into place, then remove the source."""
    tmp = dest.with_name(dest.name + ".partial")
    try:
        if src.is_dir():
            shutil.copytree(src, tmp)
        else:
            shutil.copy2(src, tmp)
        copied = file_hashes(tmp)
    except OSError as e:
        if tmp.exists():
            remove(tmp)
        raise SystemExit(f"refused: could not copy {src} to {tmp} ({e}); nothing moved") from e
    if file_hashes(src) != copied:
        remove(tmp)
        raise SystemExit(f"refused: the copy of {src} did not match it; nothing moved")
    try:
        move_no_overwrite(tmp, dest)
    except FileExistsError:
        remove(tmp)
        raise SystemExit(f"refused: {dest} appeared while copying; nothing moved") from None
    if file_hashes(src) != copied:
        raise SystemExit(f"archived to {dest}, but {src} changed meanwhile; both kept, check and remove one by hand")
    try:
        remove(src)
    except OSError as e:
        raise SystemExit(f"archived to {dest}, but {src} could not be removed ({e}); remove it by hand") from e


def archive(item: dict, folder: Path, archive_dir: Path, now: float | None = None) -> Path:
    """Move one meeting into the archive folder; refuse one that may still be written or a path outside `folder`."""
    src = folder / item["name"]
    if src.resolve().parent != folder.resolve():
        raise SystemExit(f"refused: {src} is not directly inside {folder}")
    if src.resolve() == archive_dir.resolve() or src.resolve() in archive_dir.resolve().parents:
        raise SystemExit(f"refused: the archive folder {archive_dir} is inside {src}")
    if newest_mtime(src) > (time.time() if now is None else now) - SETTLE_SECONDS:
        raise SystemExit(f"refused: {src.name} changed under {SETTLE_SECONDS}s ago; it may still be written")
    archive_dir.mkdir(parents=True, exist_ok=True)
    for _ in range(20):
        dest = free_name(archive_dir, src.name, src.is_file())
        try:
            move_no_overwrite(src, dest)
            return dest
        except FileExistsError:
            continue  # another process took the name: pick the next free one
        except OSError as e:
            if e.errno != errno.EXDEV:
                raise SystemExit(f"refused: could not move {src} to {dest} ({e}); nothing moved") from e
            copy_then_remove(src, dest)
            return dest
    raise SystemExit(f"refused: no free name for {src.name} in {archive_dir}; nothing moved")


def main(argv: list[str] | None = None) -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="meetings.py", description="List, show and archive meeting transcripts.")
    ap.add_argument("--folder", required=True, help="the transcripts folder")
    ap.add_argument("--archive", help="where processed meetings go; default <folder>/Archive")
    ap.add_argument("--root", default=str(ROOT), help="workspace root, searched for Meeting Records")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="JSON list of waiting meetings, newest first")
    sub.add_parser("show", help="one meeting's text").add_argument("key")
    sub.add_parser("archive", help="move one meeting to the archive folder").add_argument("key")
    a = ap.parse_args(argv)
    folder = Path(a.folder).expanduser()
    if not folder.is_dir():
        print(f"transcripts folder not found: {folder}", file=sys.stderr)
        return 1
    archive_dir = Path(a.archive).expanduser() if a.archive else folder / "Archive"
    root = Path(a.root)
    items = scan(folder, archive_dir, root)
    if a.cmd == "list":
        print(json.dumps([public(i) for i in items], indent=1, ensure_ascii=False))
    elif a.cmd == "show":
        item = find(items, a.key, folder)
        print(f"# {item['name']}\n\nmodified {item['modified']} | words {item['words']} | "
              f"transcript_hash {item['transcript_hash']}\n\n{transcript(folder / item['name'])}")
    else:
        print(rel(archive(find(items, a.key, folder), folder, archive_dir), root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
