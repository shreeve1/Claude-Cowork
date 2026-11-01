import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / '.claude/cowork/update.py'
ENGINE = ROOT / '.claude/cowork/update_recovery.py'


def sha(data):
    return hashlib.sha256(data).hexdigest()


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.ws = self.base / 'Workspace ü'
        self.ws.mkdir()
        self.stage = self.base / 'staging'
        self.stage.mkdir()
        self.put('config.md', b'owner\r\n')
        self.put('old/remove.md', b'retired\n')
        self.put('notes/keep.md', b'untouched\n')
        (self.ws / 'empty').mkdir()
        self.spec = {'version': 1, 'workspace': str(self.ws), 'operations': []}
        self.write('config.md', b'new\n')
        self.write('new/deep/file.md', b'added\n')
        self.spec['operations'].append({'path': 'old/remove.md', 'action': 'remove',
                                        'before_sha256': sha(b'retired\n')})
        self.engine = None

    def put(self, rel, data):
        p = self.ws / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def write(self, rel, data):
        p = self.stage / str(len(self.spec['operations']))
        p.write_bytes(data)
        before = self.ws / rel
        self.spec['operations'].append({'path': rel, 'action': 'write',
            'before_sha256': sha(before.read_bytes()) if before.exists() else None,
            'payload_path': str(p), 'after_sha256': sha(data)})

    def load(self):
        if self.engine is None:
            self.assertTrue(ENGINE.is_file(), 'controlled update engine is not implemented')
            spec = importlib.util.spec_from_file_location('cowork_update_recovery', ENGINE)
            if spec is None or spec.loader is None:
                self.fail('Cannot load controlled update engine')
            self.engine = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.engine)
        return self.engine

    def prepare(self):
        return self.load().prepare_transaction(self.ws, self.spec)

    def identifier(self, tx):
        return json.loads((tx / 'plan.json').read_text())['plan_id']

    def snapshot(self):
        return {p.relative_to(self.ws).as_posix(): p.read_bytes() if p.is_file() else None
                for p in self.ws.rglob('*') if '.workspace-backups' not in p.parts}

    def test_normal_apply_and_restore_exact_bytes_and_absence(self):
        before = self.snapshot()
        tx = self.prepare()
        e = self.load()
        e.apply_transaction(tx, self.identifier(tx))
        self.assertEqual((self.ws / 'config.md').read_bytes(), b'new\n')
        self.assertFalse((self.ws / 'old/remove.md').exists())
        e.rollback_transaction(tx, self.identifier(tx))
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(e.transaction_status(tx)['state'], 'restored')
        self.assertTrue(any(p.is_file() for p in (tx / 'quarantine').rglob('*')))

    def test_scope_paths_and_case_aliases_rejected_without_target_changes(self):
        e = self.load()
        before = self.snapshot()
        for bad in ('../escape', '/abs', 'C:/drive', 'a\\b', 'a//b', 'NUL.txt',
                    'x./file', 'file ', '.git/config', '.workspace-backups/x',
                    '.claude/skills/custom/file', 'CONFIG.md'):
            with self.subTest(bad=bad):
                spec = json.loads(json.dumps(self.spec))
                spec['operations'][0]['path'] = bad
                with self.assertRaises(e.UpdateError):
                    e.prepare_transaction(self.ws, spec)
                self.assertEqual(self.snapshot(), before)

    def test_duplicate_parent_and_unknown_fields_rejected(self):
        e = self.load()
        for extra in ({'path': 'config.md', 'action': 'remove', 'before_sha256': sha(b'owner\r\n')},
                      {'path': 'new', 'action': 'remove', 'before_sha256': sha(b'x')}):
            spec = json.loads(json.dumps(self.spec))
            spec['operations'].append(extra)
            with self.assertRaises(e.UpdateError):
                e.prepare_transaction(self.ws, spec)
        self.spec['operations'][0]['surprise'] = True
        with self.assertRaises(e.UpdateError):
            self.prepare()

    def test_links_and_hardlinks_refused(self):
        e = self.load()
        (self.ws / 'config.md').rename(self.ws / 'moved.md')
        (self.ws / 'config.md').symlink_to(self.ws / 'moved.md')
        with self.assertRaises(e.UpdateError):
            self.prepare()
        (self.ws / 'config.md').rename(self.ws / 'linked-saved')
        os.link(self.ws / 'moved.md', self.ws / 'config.md')
        with self.assertRaises(e.UpdateError):
            self.prepare()

    def test_drift_and_wrong_payload_refused(self):
        e = self.load()
        self.put('config.md', b'later owner edit')
        with self.assertRaises(e.UpdateError):
            self.prepare()
        self.put('config.md', b'owner\r\n')
        Path(self.spec['operations'][0]['payload_path']).write_bytes(b'tampered')
        with self.assertRaises(e.UpdateError):
            self.prepare()

    def test_free_space_failure_leaves_targets_unchanged(self):
        e = self.load()
        before = self.snapshot()
        with (mock.patch.object(e.shutil, 'disk_usage', return_value=type('Usage', (), {'free': 0})()),
              self.assertRaises(e.UpdateError)):
            self.prepare()
        self.assertEqual(self.snapshot(), before)

    def test_prepared_transaction_blocks_another_and_bad_approval(self):
        tx = self.prepare()
        e = self.load()
        with self.assertRaises(e.UpdateError):
            self.prepare()
        with self.assertRaises(e.UpdateError):
            e.apply_transaction(tx, 'wrong')
        e.rollback_transaction(tx, self.identifier(tx))
        self.assertEqual(e.transaction_status(tx)['state'], 'restored')
        self.prepare()

    def test_apply_revalidates_and_freezes_payload(self):
        tx = self.prepare()
        e = self.load()
        self.put('config.md', b'owner edited meanwhile')
        with self.assertRaises(e.UpdateError):
            e.apply_transaction(tx, self.identifier(tx))
        self.put('config.md', b'owner\r\n')
        for p in self.stage.iterdir():
            p.write_bytes(b'changed release')
        e.apply_transaction(tx, self.identifier(tx))
        self.assertEqual((self.ws / 'config.md').read_bytes(), b'new\n')

    def test_later_edit_or_new_owner_file_blocks_restore_without_mutation(self):
        tx = self.prepare()
        e = self.load()
        e.apply_transaction(tx, self.identifier(tx))
        self.put('config.md', b'new owner edit')
        before = self.snapshot()
        with self.assertRaises(e.UpdateError):
            e.rollback_transaction(tx, self.identifier(tx))
        self.assertEqual(self.snapshot(), before)
        self.put('config.md', b'new\n')
        self.put('new/owner.md', b'keep this')
        before = self.snapshot()
        with self.assertRaises(e.UpdateError):
            e.rollback_transaction(tx, self.identifier(tx))
        self.assertEqual(self.snapshot(), before)

    def test_corrupt_package_or_journal_stops_before_restore(self):
        tx = self.prepare()
        e = self.load()
        e.apply_transaction(tx, self.identifier(tx))
        before = self.snapshot()
        blob = tx / 'blobs' / sha(b'owner\r\n')
        old = blob.read_bytes()
        blob.write_bytes(b'damaged')
        with self.assertRaises(e.UpdateError):
            e.rollback_transaction(tx, self.identifier(tx))
        self.assertEqual(self.snapshot(), before)
        blob.write_bytes(old)
        with (tx / 'journal.jsonl').open('ab') as f:
            f.write(b'{truncated')
        with self.assertRaises(e.UpdateError):
            e.rollback_transaction(tx, self.identifier(tx))
        self.assertEqual(self.snapshot(), before)

    def test_restore_uses_retained_helper_without_staging(self):
        tx = self.prepare()
        e = self.load()
        before = self.snapshot()
        e.apply_transaction(tx, self.identifier(tx))
        self.stage.rename(self.base / 'stage-gone')
        result = subprocess.run([sys.executable, '-I', str(tx / 'restore.py'), 'rollback',
                                 str(tx), '--approved-plan', self.identifier(tx)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_successor_must_be_restored_first(self):
        first = self.prepare()
        e = self.load()
        e.apply_transaction(first, self.identifier(first))
        self.spec['predecessor'] = first.name
        self.spec['operations'] = []
        self.write('MANIFEST.json', b'{"release":5}\n')
        second = self.prepare()
        e.apply_transaction(second, self.identifier(second))
        with self.assertRaises(e.UpdateError):
            e.rollback_transaction(first, self.identifier(first))
        e.rollback_transaction(second, self.identifier(second))
        e.rollback_transaction(first, self.identifier(first))
        self.assertEqual((self.ws / 'config.md').read_bytes(), b'owner\r\n')


class UpdateCliTests(unittest.TestCase):
    def test_inspection_distinguishes_owner_content_without_writes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, ws = root / 'Release', root / 'Owner'
            source.mkdir()
            ws.mkdir()
            files = {'CLAUDE.md': b'old maintainers', 'README.md': b'new guide\n',
                     'memory/README.md': b'old layout',
                     'memory/preferences/cowork-environment.md': b'old environment',
                     'memory/schema.json': b'{}\n', '.claude/cowork/skills/index.json': b'{}\n'}
            files.update({'.claude/cowork/workspace/CLAUDE.md': b'cowork\n',
                          '.claude/cowork/workspace/cowork-environment.md': b'environment\n',
                          '.claude/skills/personal-memory/scaffold/README.md': b'layout\n'})
            for rel, data in files.items():
                target = source / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            manifest = {'release': 5, 'files': {rel: {'class': 'merge', 'sha256': sha(data)}
                                                for rel, data in files.items()}}
            manifest['files']['memory/schema.json']['class'] = 'seed'
            (source / 'MANIFEST.json').write_text(json.dumps(manifest))
            (ws / 'README.md').write_bytes(b'old guide\r\n')
            (ws / 'CLAUDE.md').write_bytes(b'cowork\r\n')
            (ws / 'memory').mkdir()
            (ws / 'memory/schema.json').write_bytes(b'{"owner":true}\n')
            (ws / 'MANIFEST.json').write_text(json.dumps({'files': {
                'README.md': {'sha256': sha(b'old guide\n')},
                'CLAUDE.md': {'sha256': sha(b'cowork\n')},
                'memory/schema.json': {'sha256': sha(b'{}\n')}}}))
            before = {p.relative_to(ws).as_posix(): p.read_bytes() for p in ws.rglob('*') if p.is_file()}
            result = subprocess.run([sys.executable, str(SCRIPT), 'inspect', str(source), str(ws)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            rows = {r['path']: r for r in json.loads(result.stdout)['files']}
            self.assertEqual(rows['README.md']['status'], 'shared_candidate')
            self.assertEqual(rows['CLAUDE.md']['status'], 'line_endings_only')
            self.assertEqual(rows['memory/schema.json']['status'], 'preserve_owner')
            self.assertFalse(rows['README.md']['approved'])
            self.assertEqual({p.relative_to(ws).as_posix(): p.read_bytes() for p in ws.rglob('*') if p.is_file()}, before)

    def test_cli_prepare_apply_status_and_persistent_restore(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ws = root / 'Owner ü'
            ws.mkdir()
            (ws / 'a.md').write_bytes(b'old')
            payload = root / 'payload'
            payload.write_bytes(b'new')
            spec = root / 'operations.json'
            spec.write_text(json.dumps({'version': 1, 'workspace': str(ws), 'operations': [
                {'path': 'a.md', 'action': 'write', 'before_sha256': sha(b'old'),
                 'after_sha256': sha(b'new'), 'payload_path': str(payload)}]}))
            def call(*args):
                result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return json.loads(result.stdout)
            prepared = call('prepare', ws, spec)
            self.assertTrue(prepared['ok'])
            tx, identifier = prepared['transaction'], prepared['plan_id']
            call('apply', tx, '--approved-plan', identifier)
            self.assertEqual(call('status', tx)['state'], 'applied')
            self.assertEqual((ws / 'a.md').read_bytes(), b'new')
            restored = subprocess.run([sys.executable, '-I', str(Path(tx) / 'restore.py'),
                                      'rollback', tx, '--approved-plan', identifier], capture_output=True, text=True)
            self.assertEqual(restored.returncode, 0, restored.stdout + restored.stderr)
            self.assertEqual((ws / 'a.md').read_bytes(), b'old')

    def test_shipped_guide_keeps_full_backup_gate_and_documents_helper(self):
        guide = (ROOT / '.claude/setup/README.md').read_text()
        self.assertIn('No user-workspace changes before verification.', guide)
        self.assertIn('UPDATE-RECOVERY.md', guide)
        self.assertIn('/.workspace-backups/', (ROOT / '.gitignore').read_text())


if __name__ == '__main__':
    unittest.main()
