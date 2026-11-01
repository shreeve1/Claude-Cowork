#!/usr/bin/env python3
"""Controlled Cowork content updates; no Windows metadata or outside-writer guarantee."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import sys
from typing import Any

STORAGE = '.workspace-backups'
HASH = re.compile(r'[0-9a-f]{64}')
TX = re.compile(r'update-[0-9a-f]{16}')
EVENTS = {'apply_begin', 'mkdir', 'apply_intent', 'apply_done', 'apply_complete',
          'restore_begin', 'restore_intent', 'restore_done', 'restore_dir', 'restore_complete'}


class UpdateError(ValueError):
    def __init__(self, code: str, path: str | Path = ''):
        self.code, self.path = code, str(path)
        super().__init__(f'{code}: {path}; stop and inspect retained recovery data')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf-8')


def relative(value, target=True):
    if not isinstance(value, str) or not value or any(c in value for c in '\\:\x00'):
        raise UpdateError('unsafe_path', value)
    for part in value.split('/'):
        if (not part or part in ('.', '..') or part[-1] in '. '
                or any(ord(c) < 32 or c in '<>"|?*' for c in part)
                or part.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL',
                    *('COM' + str(i) for i in range(1, 10)), *('LPT' + str(i) for i in range(1, 10))}):
            raise UpdateError('unsafe_path', value)
    if target and (value.split('/')[0].casefold() in {
            '.git', STORAGE, '.memory-recovery', '.task-recovery', '.agents'}
            or value.casefold().startswith(('.claude/skills/', '.claude/setup/'))
            or '.cowork-' in value.casefold()):
        raise UpdateError('protected_path', value)
    return value


def safe_path(path):
    """Reject linked ancestors and existing case aliases, including on Linux."""
    path = Path(os.path.abspath(path))
    current = Path(path.anchor)
    for part in path.parts[1:]:
        if current.exists():
            if not current.is_dir():
                raise UpdateError('not_directory', current)
            if any(n.name != part and n.name.casefold() == part.casefold() for n in current.iterdir()):
                raise UpdateError('case_alias', current / part)
        current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise UpdateError('linked_path', current)
    return path


def regular(path):
    path = safe_path(path)
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise UpdateError('not_single_regular_file', path)
    return path.read_bytes()


def file_hash(path):
    data = regular(path)
    return None if data is None else digest(data)


def directory(path):
    path = safe_path(path)
    if not path.is_dir():
        raise UpdateError('not_directory', path)
    return path


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_new(path, data):
    safe_path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as output:
        output.write(data)
        output.flush()
        os.fsync(output.fileno())
    sync_directory(path.parent)
    if regular(path) != data:
        raise UpdateError('write_verification_failed', path)


def move(source, destination):
    safe_path(source)
    safe_path(destination)
    if destination.exists():
        raise UpdateError('quarantine_collision', destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.rename(source, destination)
    sync_directory(source.parent)
    sync_directory(destination.parent)


@contextmanager
def workspace_lock(workspace):
    workspace = directory(workspace)
    storage = safe_path(workspace / STORAGE)
    storage.mkdir(exist_ok=True)
    directory(storage)
    lock = storage / 'writer.lock'
    regular(lock)
    fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise UpdateError('writer_active', workspace) from error
        yield
    finally:
        os.close(fd)


def validate_operations(workspace, document):
    workspace = directory(workspace)
    if (not isinstance(document, dict) or set(document) - {'version', 'workspace', 'predecessor', 'operations'}
            or document.get('version') != 1 or document.get('workspace') != str(workspace)):
        raise UpdateError('invalid_operation_document')
    predecessor = document.get('predecessor')
    if predecessor is not None and (not isinstance(predecessor, str) or not TX.fullmatch(predecessor)):
        raise UpdateError('invalid_predecessor')
    operations = document.get('operations')
    if not isinstance(operations, list) or not operations:
        raise UpdateError('empty_operations')
    entries = []
    folded = set()
    for operation in operations:
        if not isinstance(operation, dict):
            raise UpdateError('invalid_operation')
        action = operation.get('action')
        fields = {'path', 'action', 'before_sha256'}
        if action == 'write':
            fields |= {'payload_path', 'after_sha256'}
        if set(operation) != fields or action not in ('write', 'remove'):
            raise UpdateError('invalid_operation_fields', operation.get('path', ''))
        rel = relative(operation['path'])
        folded.add(rel.casefold())
        before = operation['before_sha256']
        if before is not None and (not isinstance(before, str) or not HASH.fullmatch(before)):
            raise UpdateError('invalid_before_hash', rel)
        data = regular(workspace / rel)
        if (None if data is None else digest(data)) != before:
            raise UpdateError('source_drift', rel)
        if action == 'remove' and before is None:
            raise UpdateError('missing_remove_target', rel)
        entry: dict[str, Any] = {'path': rel, 'action': action, 'before': before, 'after': None,
                                 'absent_dirs': [], 'before_size': len(data) if data is not None else 0}
        for parent in reversed((workspace / rel).parents):
            if workspace in parent.parents and not parent.exists():
                entry['absent_dirs'].append(parent.relative_to(workspace).as_posix())
        if action == 'write':
            after = operation['after_sha256']
            if not isinstance(after, str) or not HASH.fullmatch(after):
                raise UpdateError('invalid_payload_hash', rel)
            payload = safe_path(operation['payload_path'])
            if workspace == payload or workspace in payload.parents:
                raise UpdateError('payload_inside_workspace', rel)
            data = regular(payload)
            if data is None or digest(data) != after:
                raise UpdateError('payload_mismatch', rel)
            entry.update(after=after, payload=str(payload), after_size=len(data))
        entries.append(entry)
    if len(folded) != len(entries) or any(a != b and b.startswith(a + '/') for a in folded for b in folded):
        raise UpdateError('overlapping_paths')
    return {'entries': sorted(entries, key=lambda e: e['path']), 'predecessor': predecessor}


def load_plan(transaction):
    transaction = directory(transaction)
    if transaction.parent.name != STORAGE or not TX.fullmatch(transaction.name):
        raise UpdateError('invalid_transaction_location', transaction)
    workspace = directory(transaction.parent.parent)
    raw, seal = regular(transaction / 'plan.json'), regular(transaction / 'VERIFIED')
    if raw is None or seal is None or seal != digest(raw).encode():
        raise UpdateError('invalid_package', transaction)
    try:
        plan = json.loads(raw)
        body = {k: v for k, v in plan.items() if k != 'plan_id'}
        if (plan['format'] != 'cowork-update/1' or plan['transaction'] != transaction.name
                or plan['workspace_name'] != workspace.name or plan['plan_id'] != digest(canonical(body))):
            raise UpdateError('package_identity_mismatch', transaction)
        for e in plan['entries']:
            relative(e['path'])
            for parent in e['absent_dirs']:
                relative(parent)
                if not e['path'].startswith(parent + '/'):
                    raise UpdateError('invalid_parent_record', parent)
            for key in ('before', 'after'):
                h = e[key]
                if h is not None and (not isinstance(h, str) or not HASH.fullmatch(h)
                                      or file_hash(transaction / 'blobs' / h) != h):
                    raise UpdateError('corrupt_saved_bytes', e['path'])
        for rel, h in plan['support'].items():
            relative(rel, target=False)
            if file_hash(transaction / rel) != h:
                raise UpdateError('corrupt_recovery_support', rel)
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise UpdateError('invalid_package', transaction) from error
    return workspace, plan


def read_journal(transaction):
    data = regular(transaction / 'journal.jsonl')
    if data is None:
        return []
    if data and not data.endswith(b'\n'):
        raise UpdateError('truncated_journal', transaction)
    rows, previous = [], ''
    for line in data.splitlines():
        try:
            record = json.loads(line)
            checksum = record.pop('checksum')
            if (record['sequence'] != len(rows) or record['previous'] != previous
                    or record['event'] not in EVENTS or checksum != digest(canonical(record))):
                raise UpdateError('corrupt_journal', transaction)
        except (ValueError, KeyError, TypeError) as error:
            raise UpdateError('corrupt_journal', transaction) from error
        record['checksum'] = checksum
        rows.append(record)
        previous = checksum
    return rows


def append(transaction, rows, event, **values):
    row = dict(sequence=len(rows), previous=rows[-1]['checksum'] if rows else '', event=event, **values)
    row['checksum'] = digest(canonical(row))
    path = transaction / 'journal.jsonl'
    regular(path)
    with path.open('ab') as output:
        output.write(canonical(row) + b'\n')
        output.flush()
        os.fsync(output.fileno())
    sync_directory(transaction)
    rows.append(row)


def state(rows):
    events = [r['event'] for r in rows]
    if 'restore_complete' in events:
        return 'restored'
    if 'restore_begin' in events:
        return 'rolling-back'
    if 'apply_complete' in events:
        return 'applied'
    return 'interrupted' if 'apply_begin' in events else 'prepared'


def transaction_status(transaction):
    transaction = Path(transaction)
    _, plan = load_plan(transaction)
    return {'state': state(read_journal(transaction)), 'plan_id': plan['plan_id'],
            'transaction': str(transaction), 'file_count': len(plan['entries']),
            'metadata': 'file content and presence only; no Windows metadata guarantee'}


def records(workspace):
    storage = workspace / STORAGE
    if not storage.exists():
        return {}
    found = {}
    for child in directory(storage).iterdir():
        if TX.fullmatch(child.name):
            _, plan = load_plan(child)
            found[child.name] = (plan, state(read_journal(child)))
    return found


def check_dependency(workspace, transaction=None, predecessor=None):
    found = records(workspace)
    if transaction is not None:
        if any(p.get('predecessor') == transaction.name and s != 'restored' for p, s in found.values()):
            raise UpdateError('restore_successor_first', transaction)
        return
    active = {name: (p, s) for name, (p, s) in found.items() if s != 'restored'}
    if any(s != 'applied' for _, s in active.values()):
        raise UpdateError('unresolved_transaction', workspace)
    tips = set(active) - {p.get('predecessor') for p, _ in active.values()}
    if tips != ({predecessor} if predecessor else set()):
        raise UpdateError('predecessor_required', workspace)


def prepare_transaction(workspace, document, checkpoint=lambda _: None):
    workspace = directory(workspace)
    approved = validate_operations(workspace, document)
    entries = approved['entries']
    needed = sum(e['before_size'] + 3 * e.get('after_size', 0) for e in entries) + 131072
    if shutil.disk_usage(workspace).free < needed:
        raise UpdateError('insufficient_space', workspace)
    with workspace_lock(workspace):
        check_dependency(workspace, predecessor=approved['predecessor'])
        suffix = secrets.token_hex(8)
        destination = workspace / STORAGE / ('update-' + suffix)
        transaction = workspace / STORAGE / ('.preparing-' + suffix)
        transaction.mkdir(mode=0o700)
        checkpoint('prepare_created')
        (transaction / 'blobs').mkdir()
        support = {}
        helper = Path(__file__).read_bytes()
        write_new(transaction / 'restore.py', helper)
        support['restore.py'] = digest(helper)
        index = '.claude/cowork/skills/index.json'
        old_index = regular(workspace / index)
        if old_index is not None:
            target = transaction / 'baseline' / index
            target.parent.mkdir(parents=True)
            write_new(target, old_index)
            support['baseline/' + index] = digest(old_index)
        for e in entries:
            pairs = [('before', regular(workspace / e['path'])),
                     ('after', regular(Path(e['payload'])) if 'payload' in e else None)]
            for name, data in pairs:
                if (None if data is None else digest(data)) != e[name]:
                    raise UpdateError('source_drift', e['path'])
                if data is not None and not (transaction / 'blobs' / e[name]).exists():
                    write_new(transaction / 'blobs' / e[name], data)
            e.pop('payload', None)
        plan = {'format': 'cowork-update/1', 'transaction': destination.name, 'workspace_name': workspace.name,
                'predecessor': approved['predecessor'], 'entries': entries, 'support': support}
        plan['plan_id'] = digest(canonical(plan))
        raw = canonical(plan)
        write_new(transaction / 'plan.json', raw)
        write_new(transaction / 'README-RESTORE.txt', (
            'Retain this whole folder. Stop outside editing. With explicit restore approval run:\n'
            f'python3 restore.py rollback "<this folder>" --approved-plan {plan["plan_id"]}\n'
            'Content/presence only. Saved skill cards and Git commits are separate.\n').encode())
        write_new(transaction / 'VERIFIED', digest(raw).encode())
        move(transaction, destination)
        load_plan(destination)
        return destination


def temp_path(workspace, transaction, i, phase):
    rel = json.loads((transaction / 'plan.json').read_bytes())['entries'][i]['path']
    return (workspace / rel).with_name(f'.cowork-{transaction.name}-{i}-{phase}.tmp')


def quarantine(transaction, kind, i):
    return transaction / 'quarantine' / kind / str(i)


def checkpoint_none(_):
    pass


def apply_transaction(transaction, approved_plan, checkpoint=checkpoint_none):
    transaction = directory(transaction)
    workspace, plan = load_plan(transaction)
    if approved_plan != plan['plan_id']:
        raise UpdateError('approval_mismatch', transaction)
    with workspace_lock(workspace):
        load_plan(transaction)
        check_dependency(workspace, transaction)
        rows = read_journal(transaction)
        if rows:
            raise UpdateError('already_started_restore_first', transaction)
        for e in plan['entries']:
            if file_hash(workspace / e['path']) != e['before']:
                raise UpdateError('source_drift', e['path'])
            for parent in e['absent_dirs']:
                if safe_path(workspace / parent).exists():
                    raise UpdateError('new_parent_appeared', parent)
        append(transaction, rows, 'apply_begin')
        for i, e in enumerate(plan['entries']):
            target = workspace / e['path']
            if file_hash(target) != e['before']:
                raise UpdateError('source_drift', e['path'])
            if e['action'] == 'write':
                for parent in e['absent_dirs']:
                    path = safe_path(workspace / parent)
                    if not path.exists():
                        append(transaction, rows, 'mkdir', path=parent)
                        path.mkdir()
                        sync_directory(path.parent)
                tmp = temp_path(workspace, transaction, i, 'apply')
                if tmp.exists():
                    raise UpdateError('unexpected_temp', tmp)
                append(transaction, rows, 'apply_intent', index=i)
                checkpoint('apply_intent:' + e['path'])
                try:
                    write_new(tmp, regular(transaction / 'blobs' / e['after']))
                except OSError:
                    if tmp.exists():
                        move(tmp, quarantine(transaction, 'failed-writes-' + secrets.token_hex(4), i))
                    raise
                checkpoint('apply_temp:' + e['path'])
                os.replace(tmp, target)
                sync_directory(target.parent)
                checkpoint('apply_write:' + e['path'])
            else:
                append(transaction, rows, 'apply_intent', index=i)
                checkpoint('apply_intent:' + e['path'])
                move(target, quarantine(transaction, 'removed', i))
                checkpoint('apply_remove:' + e['path'])
            append(transaction, rows, 'apply_done', index=i)
        for e in plan['entries']:
            if file_hash(workspace / e['path']) != e['after']:
                raise UpdateError('apply_verification_failed', e['path'])
        append(transaction, rows, 'apply_complete')
        checkpoint('apply_complete')
    return transaction_status(transaction)


def restore_preflight(workspace, transaction, plan, rows):
    entries = plan['entries']
    applied = {r['index'] for r in rows if r['event'] == 'apply_intent'}
    restoring = {r['index'] for r in rows if r['event'] == 'restore_intent'}
    created = {r['path'] for r in rows if r['event'] == 'mkdir'}
    declared_dirs = {d for e in entries for d in e['absent_dirs']}
    if not created <= declared_dirs or not restoring <= applied or any(
            not isinstance(i, int) or i < 0 or i >= len(entries) for i in applied | restoring):
        raise UpdateError('invalid_journal_scope', transaction)
    allowed = {e['path'] for e in entries} | created
    for i, e in enumerate(entries):
        current = file_hash(workspace / e['path'])
        displaced = file_hash(quarantine(transaction, 'displaced', i))
        removed = file_hash(quarantine(transaction, 'removed', i))
        if displaced is not None and (i not in restoring or displaced != e['after']):
            raise UpdateError('displaced_bytes_changed', e['path'])
        if removed is not None and (i not in applied or e['action'] != 'remove' or removed != e['before']):
            raise UpdateError('removed_bytes_changed', e['path'])
        if current != e['before']:
            normal = i in applied and current == e['after']
            gap = i in restoring and current is None and displaced == e['after'] and e['after'] is not None
            if not normal and not gap:
                raise UpdateError('later_edit_conflict', e['path'])
            if e['action'] == 'remove' and removed != e['before']:
                raise UpdateError('missing_retained_removal', e['path'])
        for phase, expected, owned in [('apply', e['after'], i in applied),
                                       ('restore', e['before'], i in restoring)]:
            tmp = temp_path(workspace, transaction, i, phase)
            h = file_hash(tmp)
            if h is not None:
                if not owned or h != expected or expected is None:
                    raise UpdateError('changed_or_unowned_temp', tmp)
                allowed.add(tmp.relative_to(workspace).as_posix())
    for d in declared_dirs:
        path = safe_path(workspace / d)
        if not path.exists():
            continue
        if d not in created or not path.is_dir():
            raise UpdateError('new_parent_conflict', d)
        for child in path.rglob('*'):
            safe_path(child)
            rel = child.relative_to(workspace).as_posix()
            if rel not in allowed:
                raise UpdateError('owner_content_in_new_folder', rel)
    return restoring, created


def rollback_transaction(transaction, approved_plan, checkpoint=checkpoint_none):
    transaction = directory(transaction)
    workspace, plan = load_plan(transaction)
    if approved_plan != plan['plan_id']:
        raise UpdateError('approval_mismatch', transaction)
    with workspace_lock(workspace):
        load_plan(transaction)
        check_dependency(workspace, transaction)
        rows = read_journal(transaction)
        restoring, created = restore_preflight(workspace, transaction, plan, rows)
        if state(rows) == 'restored':
            return transaction_status(transaction)
        append(transaction, rows, 'restore_begin')
        for i, e in enumerate(plan['entries']):
            target = workspace / e['path']
            current = file_hash(target)
            if current != e['before']:
                tmp = temp_path(workspace, transaction, i, 'restore')
                if i not in restoring:
                    append(transaction, rows, 'restore_intent', index=i)
                checkpoint('restore_intent:' + e['path'])
                if e['before'] is not None:
                    if not tmp.exists():
                        try:
                            write_new(tmp, regular(transaction / 'blobs' / e['before']))
                        except OSError:
                            if tmp.exists():
                                move(tmp, quarantine(transaction, 'failed-writes-' + secrets.token_hex(4), i))
                            raise
                    checkpoint('restore_temp:' + e['path'])
                if current is not None:
                    move(target, quarantine(transaction, 'displaced', i))
                    checkpoint('restore_move:' + e['path'])
                if e['before'] is not None:
                    os.replace(tmp, target)
                    sync_directory(target.parent)
                    checkpoint('restore_write:' + e['path'])
                append(transaction, rows, 'restore_done', index=i)
            for phase in ('apply', 'restore'):
                tmp = temp_path(workspace, transaction, i, phase)
                if tmp.exists():
                    move(tmp, quarantine(transaction, phase + '-temps', i))
        for d in sorted(created, key=lambda s: (s.count('/'), s)):
            path = workspace / d
            if not path.exists():
                continue
            if any(p.is_file() for p in path.rglob('*')):
                raise UpdateError('created_folder_not_empty', d)
            index = sorted(created).index(d)
            append(transaction, rows, 'restore_dir', path=d)
            move(path, quarantine(transaction, 'directories', index))
            checkpoint('restore_dir:' + d)
        for e in plan['entries']:
            if file_hash(workspace / e['path']) != e['before']:
                raise UpdateError('restore_verification_failed', e['path'])
        if any((workspace / d).exists() for d in created):
            raise UpdateError('original_absence_not_restored')
        checkpoint('restore_complete')
        append(transaction, rows, 'restore_complete')
    return transaction_status(transaction)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('apply', 'rollback', 'status'):
        p = sub.add_parser(command)
        p.add_argument('transaction', type=Path)
        if command != 'status':
            p.add_argument('--approved-plan', required=True)
    args = parser.parse_args(argv)
    try:
        function = {'apply': apply_transaction, 'rollback': rollback_transaction, 'status': transaction_status}[args.command]
        values = (args.transaction,) if args.command == 'status' else (args.transaction, args.approved_plan)
        print(json.dumps({'ok': True, **function(*values)}))
        return 0
    except (UpdateError, OSError, ValueError) as error:
        print(json.dumps({'ok': False, 'error': getattr(error, 'code', 'filesystem_error'),
                          'path': getattr(error, 'path', ''), 'next': 'Stop; retain recovery files and inspect before retrying.'}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
