#!/usr/bin/env python3
"""Retention sweep for the work folders no other rule prunes.

Lists files past their age limit; --apply deletes them and any folder that deletion left empty.
A file under `artifacts/` is kept while a note, skill or context file names it or its topic folder.
`reports/`, `memory/` and `clients/` are never touched here: memory has its own rules (gate.py).
Only a file whose bytes equal the committed copy is deleted, so every deletion can be undone.
Any doubt (not a git repo, a nested root, an unreadable folder) deletes nothing.
"""

import argparse
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import unquote

DAY = 86400
# folder, max age in days, keep a file that a text names, subfolders left alone (runtime state with its own lifecycle)
RULES = (
    (".sessions", 90, False, ()),
    ("artifacts", 90, True, ("artifacts/startday",)),
)
CORPUS_ROOTS = ("memory", ".claude", "CONTEXT.md", "CLAUDE.md")
CORPUS_SUFFIXES = {".md", ".py", ".json"}
CORPUS_SKIP = {"node_modules", "__pycache__", ".venv", ".git"}


def _raise(error):
    raise error


def corpus(root):
    """Every text that may name an artifact, as one string, plus its URL-decoded form.
    An unreadable folder or file raises: no guess is safe."""
    parts = []
    for name in CORPUS_ROOTS:
        base = root / name
        if base.is_file():
            parts.append(base.read_text(encoding="utf-8", errors="replace"))
        elif base.is_dir():
            for dirpath, dirnames, filenames in os.walk(base, onerror=_raise):
                dirnames[:] = [d for d in dirnames if d not in CORPUS_SKIP]
                for f in filenames:
                    if Path(f).suffix in CORPUS_SUFFIXES:
                        parts.append(
                            (Path(dirpath) / f).read_text(encoding="utf-8", errors="replace")
                        )
    text = "\n".join(parts)
    return text + "\n" + unquote(text)


def referenced(rel, text):
    """True when `rel` or an ancestor below the top folder (artifacts/<topic>) appears in `text` as a whole path."""
    parts = rel.split("/")
    for i in range(2, len(parts) + 1):
        pattern = re.escape("/".join(parts[:i])) + r"(?![\w-]|\.\w)"
        if re.search(pattern, text):
            return True
    return False


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True)


def tracked_paths(root):
    """Paths git tracks, or None when the root is not the top of a git repo."""
    prefix = git(root, "rev-parse", "--show-prefix")
    if prefix.returncode or prefix.stdout.strip():
        return None
    tracked = git(root, "ls-files", "-z")
    if tracked.returncode:
        return None
    return {os.fsdecode(p) for p in tracked.stdout.split(b"\0") if p}


def matches_head(root, rel, path=None):
    """True when the file's raw bytes equal the blob HEAD holds for `rel`, and the file did not change while it
    was read. Raw bytes, not `git hash-object`: its clean filter (CRLF, ident) can make an edited file look
    identical. Ignores assume-unchanged and skip-worktree flags, so it proves the commit can restore the file."""
    path = path or root / rel
    blob = git(root, "cat-file", "blob", f"HEAD:{rel}")
    if blob.returncode:
        return False
    try:
        before = os.lstat(path)
        data = path.read_bytes()
        after = os.lstat(path)
    except OSError:
        return False
    stable = (before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    )
    return stable and data == blob.stdout


def candidates(root, now):
    """(relative path, age in days, size) of every file past its limit, unprotected and tracked."""
    keep = tracked_paths(root)
    if keep is None:
        return []
    text = None
    found = []
    for folder, days, keep_named, skip in RULES:
        base = root / folder
        if base.is_symlink() or not base.is_dir():
            continue
        for dirpath, _, filenames in os.walk(base, followlinks=False, onerror=_raise):
            for name in filenames:
                p = Path(dirpath) / name
                rel = p.relative_to(root).as_posix()
                if (
                    p.is_symlink()
                    or not p.is_file()
                    or rel not in keep
                    or any(rel == s or rel.startswith(s + "/") for s in skip)
                ):
                    continue
                st = p.stat()
                age = (now - st.st_mtime) / DAY
                if age <= days:
                    continue
                if keep_named:
                    text = corpus(root) if text is None else text
                    if referenced(rel, text):
                        continue
                found.append((rel, int(age), st.st_size))
    return sorted(found)


def delete_if_restorable(root, rel):
    """Move the file aside (one atomic rename), compare it with the committed copy, then delete it.
    A file that differs goes back under its own name. Returns (deleted, note)."""
    path = root / rel
    aside = path.with_name(f"{path.name}.sweep-{uuid.uuid4().hex}")
    try:
        os.rename(path, aside)
    except OSError as e:
        return False, f"could not move aside ({e})"
    if matches_head(root, rel, aside):
        aside.unlink()
        return True, ""
    try:
        os.link(aside, path)
    except FileExistsError:
        return (
            False,
            f"changed since it was listed; its text is kept as {aside.relative_to(root).as_posix()}",
        )
    except OSError as e:
        return (
            False,
            f"changed since it was listed; its text is kept as {aside.relative_to(root).as_posix()} ({e})",
        )
    aside.unlink()
    return False, "changed since it was listed; left in place"


def prune_empty(root, deleted):
    """Remove folders a deletion emptied, walking up from each deleted file; the rule folders themselves stay."""
    tops = {folder for folder, *_ in RULES}
    for rel in deleted:
        parent = Path(rel).parent
        while parent.as_posix() not in tops and parent.as_posix() != ".":
            try:
                os.rmdir(root / parent)
            except OSError:
                break
            parent = parent.parent


def main():
    ap = argparse.ArgumentParser(description="Delete work-folder files past their retention age.")
    ap.add_argument("--root", default=".", help="Workspace root (default: current folder)")
    ap.add_argument("--apply", action="store_true", help="Delete; without it, list only")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    try:
        found = candidates(root, time.time())
    except OSError as e:
        print(f"sweep: stopped, nothing deleted ({e})")
        sys.exit(2)
    done, size = [], 0
    for rel, age, nbytes in found:
        if args.apply:
            deleted, note = delete_if_restorable(root, rel)
            if not deleted:
                print(f"skipped {rel}: {note}")
                continue
        print(f"{'deleted' if args.apply else 'would delete'} {rel} ({age} days old)")
        done.append(rel)
        size += nbytes
    if args.apply:
        prune_empty(root, done)
    print(
        f"sweep: {len(done)} files, {size} bytes{'' if args.apply else ' (dry run; --apply deletes)'}"
    )


if __name__ == "__main__":
    main()
