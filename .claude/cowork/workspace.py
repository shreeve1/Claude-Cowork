#!/usr/bin/env python3
"""Select Cowork user files from an extracted Release; never copy skill sources.

plan SOURCE prints a projected manifest with source paths for approved updates.
create SOURCE DEST creates a fresh workspace only; it never updates an existing one.
"""

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path, PurePosixPath

OVERRIDES = {
    "CLAUDE.md": ".claude/cowork/workspace/CLAUDE.md",
    "memory/README.md": ".claude/skills/personal-memory/scaffold/README.md",
    "memory/rules.md": ".claude/cowork/workspace/rules.md",
    "memory/index.md": ".claude/cowork/workspace/index.md",
}
REFERENCE_FILES = {"START-HERE.md", "memory/preferences/cowork-environment.md"}
ROOT_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CLAUDE.md",
    "CONTEXT.md",
    ".gitignore",
    ".gitattributes",
}
HOOKS = {
    ".githooks/pre-commit",
    ".githooks/commit-msg",
    ".githooks/secret-allow.json",
    ".githooks/nopython/commit-msg",
}
INDEX = ".claude/cowork/skills/index.json"


def source_file(root, relative):
    parts = PurePosixPath(relative).parts
    if (
        not parts
        or relative != "/".join(parts)
        or parts[0].startswith("/")
        or any(p in (".", "..") for p in parts)
        or "\\" in relative
        or ":" in relative
    ):
        raise ValueError(f"unsafe Release path: {relative}")
    path = root.joinpath(*parts)
    if not path.resolve().is_relative_to(root) or any(
        p.is_symlink() for p in (path, *path.parents) if p != root.parent
    ):
        raise ValueError(f"unsafe linked Release file: {relative}")
    if not path.is_file():
        raise ValueError(f"Release file missing: {relative}")
    return path


def selected(relative):
    return relative not in REFERENCE_FILES and (
        relative in ROOT_FILES
        or relative in HOOKS
        or relative == INDEX
        or relative.startswith(("memory/", "tasks/", "projects/"))
    )


def project(source):
    manifest = json.loads(source_file(source, "MANIFEST.json").read_text(encoding="utf-8"))
    files = {}
    for relative, meta in manifest["files"].items():
        source_file(source, relative)
        if not selected(relative):
            continue
        original = OVERRIDES.get(relative, relative)
        path = source_file(source, original)
        files[relative] = dict(
            meta,
            source=original,
            sha256=hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        )
    for relative in (*OVERRIDES, INDEX):
        if relative not in files:
            raise ValueError(f"Release manifest missing required user file: {relative}")
    return {**manifest, "files": dict(sorted(files.items()))}


def create(source, destination, manifest):
    if destination.is_symlink():
        raise ValueError("destination must not be a symlink")
    destination = destination.resolve()
    if destination.is_relative_to(source) or source.is_relative_to(destination):
        raise ValueError("source and destination must be separate")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("destination must be a new or empty directory")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f".{destination.name}-", dir=destination.parent
    ) as temporary:
        staged = Path(temporary) / "workspace"
        staged.mkdir()
        for relative, meta in manifest["files"].items():
            target = staged / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as output:
                output.write(source_file(source, meta["source"]).read_bytes())
            target.chmod(int(meta.get("mode", "644"), 8))
        installed = {
            **manifest,
            "files": {
                relative: {key: value for key, value in meta.items() if key != "source"}
                for relative, meta in manifest["files"].items()
            },
        }
        with (staged / "MANIFEST.json").open("x", encoding="utf-8", newline="\n") as output:
            json.dump(installed, output, indent=1)
            output.write("\n")
        if destination.exists():
            destination.rmdir()
        staged.rename(destination)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan")
    plan.add_argument("source")
    fresh = commands.add_parser("create")
    fresh.add_argument("source")
    fresh.add_argument("destination")
    args = parser.parse_args(argv)
    try:
        source = Path(args.source).resolve()
        manifest = project(source)
        if args.command == "plan":
            print(json.dumps(manifest, indent=1))
        else:
            create(source, Path(args.destination), manifest)
            print(f"Created Cowork workspace: {Path(args.destination).resolve()}")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"workspace: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
