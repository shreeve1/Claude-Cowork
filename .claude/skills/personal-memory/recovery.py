#!/usr/bin/env python3
"""Backup only: preserve exact previous memory bytes before an agent edits them."""
import argparse
import sys
from pathlib import Path
from uuid import uuid4


def reject_symlinks(path: Path) -> None:
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('symlink components are not allowed')


class SourceChangedError(OSError):
    """A complete snapshot exists, but the source is no longer safe to edit."""


def snapshot(root: Path, relative_path: str) -> Path:
    parts = relative_path.split('/')
    if not parts or parts[0] != 'memory':
        raise ValueError("expected a POSIX workspace-relative memory/ file path")
    return snapshot_memory(root / "memory", "/".join(parts[1:]))


def snapshot_memory(memory_dir: Path, relative_path: str) -> Path:
    """Preserve a file under the explicitly selected memory root, including --memory overrides."""
    memory_dir = memory_dir.absolute()
    root = memory_dir.parent
    if memory_dir.is_symlink() or root.is_symlink():
        raise ValueError("workspace root must not be a symlink")
    root = root.resolve()
    parts = relative_path.split('/')
    if (not relative_path or '\\' in relative_path
            or ':' in relative_path or any(p in ('', '.', '..') for p in parts)):
        raise ValueError('expected a POSIX workspace-relative memory/ file path')
    parts = [memory_dir.name, *parts]
    source = root.joinpath(*parts)
    reject_symlinks(source)
    if not source.exists():
        raise FileNotFoundError('memory source does not exist')
    if not source.is_file():
        raise ValueError('memory source must be a regular file')
    recovery = root / '.memory-recovery'
    reject_symlinks(recovery)
    original = source.read_bytes()
    recovery.mkdir(exist_ok=True)
    directory = recovery / uuid4().hex
    directory.mkdir()
    target = directory.joinpath(*parts)
    created = False
    verified = False
    try:
        target.parent.mkdir(parents=True)
        reject_symlinks(target)
        with target.open('xb') as stream:
            created = True
            stream.write(original)
        if target.read_bytes() != original:
            raise OSError('snapshot verification failed')
        verified = True
        reject_symlinks(source)
        if source.read_bytes() != original:
            raise SourceChangedError(f"source changed; stop editing and re-read. Verified snapshot retained: {target}")
        return target
    except (OSError, ValueError):
        if created and not verified:
            target.unlink()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    commands = parser.add_subparsers(dest='command', required=True)
    command = commands.add_parser('snapshot')
    command.add_argument('path')
    args = parser.parse_args()
    try:
        saved = snapshot(args.root, args.path)
    except SourceChangedError as exc:
        print(f"Snapshot failed: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError):
        print('Snapshot failed: invalid path, unavailable source or failed verification; stop editing.', file=sys.stderr)
        return 1
    print(f'Snapshot saved: {saved}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
