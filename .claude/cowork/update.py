#!/usr/bin/env python3
"""Inspect a staged Cowork release; prepare/apply approved content changes.

Experimental: the normal setup flow still requires its verified full backup.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

def sibling(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + '.py'))
    if spec is None or spec.loader is None:
        raise ImportError(f'Missing updater component: {name}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


recovery = sibling('update_recovery')
projection = sibling('workspace')


def normalized(data):
    return recovery.digest(data.replace(b'\r\n', b'\n'))


def inspect_release(source, workspace):
    source, workspace = recovery.directory(source), recovery.directory(workspace)
    if source == workspace or source in workspace.parents or workspace in source.parents:
        raise recovery.UpdateError('release_workspace_overlap')
    manifest = projection.project(source)
    raw = recovery.regular(workspace / 'MANIFEST.json')
    baseline = json.loads(raw) if raw is not None else {'files': {}}
    old_files = baseline.get('files', {})
    if not isinstance(old_files, dict):
        raise recovery.UpdateError('invalid_baseline_manifest')
    rows = []
    for rel, meta in manifest['files'].items():
        recovery.relative(rel)
        data = recovery.regular(workspace / rel)
        desired = recovery.regular(source / meta['source'])
        kind = meta.get('class')
        old = old_files.get(rel, {})
        if data is None:
            status = 'missing_candidate'
        elif data == desired:
            status = 'unchanged'
        elif normalized(data) == normalized(desired):
            status = 'line_endings_only'
        elif kind in ('seed', 'local'):
            status = 'preserve_owner'
        elif isinstance(old, dict) and old.get('sha256') == normalized(data):
            status = 'shared_candidate'
        else:
            status = 'owner_conflict'
        rows.append({'path': rel, 'status': status, 'class': kind, 'approved': False,
                     'before_sha256': None if data is None else recovery.digest(data),
                     'source': meta['source'], 'bytes': 0 if data is None else len(data)})
    for rel in sorted(set(old_files) - set(manifest['files'])):
        recovery.relative(rel, target=False)
        rows.append({'path': rel, 'status': 'obsolete_review_only', 'approved': False})
    return {'ok': True, 'release': manifest.get('release'), 'workspace': str(workspace),
            'files': rows, 'note': 'Read-only candidates, not replacement or removal approval. '
                                  'Unlisted workspace files are not scanned and must remain untouched.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    inspect = commands.add_parser('inspect')
    inspect.add_argument('source', type=Path)
    inspect.add_argument('workspace', type=Path)
    prepare = commands.add_parser('prepare')
    prepare.add_argument('workspace', type=Path)
    prepare.add_argument('operations', type=Path)
    for name in ('apply', 'rollback', 'status'):
        command = commands.add_parser(name)
        command.add_argument('transaction', type=Path)
        if name != 'status':
            command.add_argument('--approved-plan', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'inspect':
            result = inspect_release(args.source, args.workspace)
        elif args.command == 'prepare':
            document = json.loads(recovery.regular(args.operations))
            tx = recovery.prepare_transaction(args.workspace, document)
            result = recovery.transaction_status(tx)
            result['operations'] = recovery.load_plan(tx)[1]['entries']
            result['package_bytes'] = sum(p.stat().st_size for p in tx.rglob('*') if p.is_file())
        elif args.command == 'status':
            result = recovery.transaction_status(args.transaction)
        else:
            function = recovery.apply_transaction if args.command == 'apply' else recovery.rollback_transaction
            result = function(args.transaction, args.approved_plan)
        print(json.dumps({'ok': True, **result}, indent=1))
        return 0
    except (recovery.UpdateError, OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({'ok': False, 'error': getattr(error, 'code', 'invalid_input_or_filesystem'),
                          'path': getattr(error, 'path', ''),
                          'next': 'Stop; retain recovery data. Inspect the named path before another change.'}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
