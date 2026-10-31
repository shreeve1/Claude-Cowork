#!/usr/bin/env python3
"""Read-only structural checks for shared procedures; approval remains an owner decision."""
import re
from datetime import date
from pathlib import Path

import hubs
import schema


def unsafe_path(path: Path, boundary: Path | None = None) -> bool:
    path = path.absolute()
    boundary = boundary.absolute() if boundary is not None else path.parents[2]
    current = path
    while True:
        if current.is_symlink():
            return True
        if current == boundary:
            return False
        current = current.parent


def validate(path: Path, today: date | None = None) -> list[str]:
    today = today or date.today()
    if unsafe_path(path) or not path.is_file():
        return [f"{path}: expected a regular file without symlink components"]
    fields = hubs.parse_frontmatter(path)
    problems = []
    if fields.get('type') != 'procedure':
        problems.append(f"{path}: requires type: procedure")
    risk = fields.get('risk')
    if risk not in ('read-only', 'changes-state'):
        problems.append(f"{path}: risk must be read-only or changes-state")
    for key in ('approved', 'verified'):
        value = fields.get(key, '')
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) or date.fromisoformat(value) > today:
                raise ValueError
        except ValueError:
            problems.append(f"{path}: {key} requires a real YYYY-MM-DD date, not in the future")
    sections = {}
    current = None
    parent = None
    fence = None
    text = hubs.read_note(path)
    if text.startswith('---\n'):
        end = text.find('\n---', 4)
        text = text[end + 4:] if end != -1 else ''
    for line in text.splitlines():
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if marker:
            delimiter = marker[1]
            if fence is None:
                fence = delimiter
            elif delimiter[0] == fence[0] and len(delimiter) >= len(fence) and not line.strip().strip(delimiter[0]):
                fence = None
            continue
        if fence:
            continue
        heading = re.match(r'^(#{1,6})\s+(.+?)\s*#*\s*$', line)
        if heading:
            level = len(heading[1])
            if level <= 2:
                parent = heading[2] if level == 2 else None
            current = (level, heading[2])
            if level != 2 and not (level == 3 and parent == "Active memory"):
                current = None
            if current:
                sections.setdefault(current, [])
        elif current:
            sections[current].append(line)
    required = [(2, 'Active memory'), (3, 'Prerequisites'), (3, 'Steps'),
                (3, 'Verify'), (2, 'Related'), (2, 'Notes')]
    if risk == 'changes-state':
        required += [(3, 'Approval'), (3, 'Recovery')]
    for key in required:
        if not '\n'.join(sections.get(key, [])).strip():
            problems.append(f"{path}: requires nonempty {'#' * key[0]} {key[1]}")
    if not re.search(r'^Trigger:[ \t]*[^\s].*$', '\n'.join(sections.get((2, 'Active memory'), [])), re.M):
        problems.append(f"{path}: Active memory requires Trigger: text")
    if not re.search(r'^\s*\d+[.)]\s+\S', '\n'.join(sections.get((3, 'Steps'), [])), re.M):
        problems.append(f"{path}: Steps requires a numbered action")
    return problems


def selected(memory_dir: Path, relative_path: str, today: date | None = None) -> list[str]:
    parts = relative_path.split('/')
    topics = schema.load(memory_dir)['topics']
    if (len(parts) != 4 or parts[:2] != ['memory', 'workflows']
            or not isinstance(topics, list) or parts[2] not in topics
            or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', parts[2])
            or not parts[3].endswith('.md') or parts[3] in ('.', '..')
            or '\\' in relative_path or ':' in relative_path):
        return [f'{relative_path}: invalid procedure target']
    path = memory_dir.joinpath(*parts[1:])
    return validate(path, today)


def audit(memory_dir: Path, today: date | None = None) -> list[str]:
    problems = []
    base = memory_dir / 'workflows'
    if unsafe_path(base, memory_dir):
        return [f"{base}: symlink components are not allowed"]
    topics = schema.load(memory_dir)['topics']
    if not isinstance(topics, list):
        return [f'{base}: invalid workflow topic list']
    for topic in topics:
        if not isinstance(topic, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', topic):
            problems.append(f'{base}: invalid workflow topic {topic!r}')
            continue
        folder = base / topic
        if unsafe_path(folder, memory_dir):
            problems.append(f"{folder}: symlink components are not allowed")
            continue
        for path in sorted(folder.glob('*.md')):
            if unsafe_path(path, memory_dir):
                problems.append(f"{path}: symlink components are not allowed")
            elif hubs.parse_frontmatter(path).get('type') == 'procedure':
                problems.extend(validate(path, today))
    return problems
