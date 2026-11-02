import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / '.claude/cowork/workspace.py'


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'Release ü'
        self.source.mkdir()
        self.files = {
            'CLAUDE.md': 'maintainer instructions',
            'README.md': 'owner guide',
            'START-HERE.md': 'agent setup reference',
            'memory/rules.md': 'maintainer environment routing',
            'memory/index.md': 'maintainer environment index',
            'memory/README.md': 'maintainer memory guide',
            'memory/schema.json': '{}',
            'memory/preferences/cowork-environment.md': 'maintainer environment',
            'tasks/index.md': '# Active tasks\n',
            'projects/README.md': '# Projects\n',
            '.gitignore': '/.memory-recovery/\n/.task-recovery/\n',
            '.githooks/pre-commit': '#!/usr/bin/env python3\n',
            '.githooks/tests/test_hook.py': 'maintainer tests',
            '.claude/skills/professional-guidance/agent-personas/a.txt': 'persona',
            '.claude/skills/personal-memory/scaffold/README.md': 'installed skill memory guide',
            '.claude/cowork/workspace/CLAUDE.md': 'Cowork instructions',
            '.claude/cowork/workspace/rules.md': 'owner routing',
            '.claude/cowork/workspace/index.md': 'owner index',
            '.claude/cowork/workspace/cowork-environment.md': 'Cowork environment',
            '.claude/cowork/skills/index.json': '{}',
            '.claude/cowork/skills/core/personal-memory.skill': 'package',
            '.claude/setup/README.md': 'setup',
            'docs/testing/receipt.md': 'maintainer receipt',
            'CODING_STANDARDS.md': 'maintainer standards',
        }
        for rel, text in self.files.items():
            path = self.source / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
        manifest = {'edition': 'friends', 'release': 5, 'files': {
            rel: {'class': 'merge', 'mode': '644', 'sha256': 'unused'} for rel in self.files
        }}
        (self.source / 'MANIFEST.json').write_text(json.dumps(manifest), encoding='utf-8')
        self.dest = self.root / 'Workspace ü'

    def run_command(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)

    def test_create_copies_only_user_files_and_projects_manifest(self):
        result = self.run_command('create', self.source, self.dest)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.dest / 'CLAUDE.md').read_text(), 'Cowork instructions')
        self.assertEqual((self.dest / 'memory/README.md').read_text(), 'installed skill memory guide')
        self.assertEqual((self.dest / 'memory/rules.md').read_text(), 'owner routing')
        self.assertEqual((self.dest / 'memory/index.md').read_text(), 'owner index')
        for rel in ('START-HERE.md', 'memory/preferences/cowork-environment.md'):
            self.assertFalse((self.dest / rel).exists(), rel)
        self.assertTrue((self.dest / '.githooks/pre-commit').is_file())
        self.assertTrue((self.dest / '.claude/cowork/skills/index.json').is_file())
        for rel in ['.claude/skills', '.claude/setup', '.claude/cowork/skills/core', '.githooks/tests', 'docs', 'CODING_STANDARDS.md']:
            self.assertFalse((self.dest / rel).exists(), rel)
        man = json.loads((self.dest / 'MANIFEST.json').read_text())
        self.assertEqual(man['files']['CLAUDE.md']['sha256'], hashlib.sha256(b'Cowork instructions').hexdigest())
        for rel in ('START-HERE.md', 'memory/preferences/cowork-environment.md'):
            self.assertNotIn(rel, man['files'])
        self.assertNotIn('.claude/skills/professional-guidance/agent-personas/a.txt', man['files'])
        self.assertEqual((self.source / 'CLAUDE.md').read_text(), 'maintainer instructions')
        self.assertTrue((self.dest / 'tasks/index.md').is_file())

    def test_plan_does_not_modify_existing_owner_content(self):
        self.dest.mkdir()
        (self.dest / 'owner.md').write_text('keep')
        for rel in ('START-HERE.md', 'memory/preferences/cowork-environment.md'):
            target = self.dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'owner content\r\n')
        result = self.run_command('plan', self.source)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        paths = json.loads(result.stdout)['files']
        self.assertEqual(paths['CLAUDE.md']['source'], '.claude/cowork/workspace/CLAUDE.md')
        self.assertNotIn('.claude/skills/professional-guidance/agent-personas/a.txt', paths)
        self.assertEqual((self.dest / 'owner.md').read_text(), 'keep')
        for rel in ('START-HERE.md', 'memory/preferences/cowork-environment.md'):
            self.assertNotIn(rel, paths)
            self.assertEqual((self.dest / rel).read_bytes(), b'owner content\r\n')

    def test_reference_files_are_not_required_to_create_or_plan(self):
        manifest_path = self.source / 'MANIFEST.json'
        manifest = json.loads(manifest_path.read_text())
        for relative in ('START-HERE.md', 'memory/preferences/cowork-environment.md'):
            (self.source / relative).unlink()
            del manifest['files'][relative]
        manifest_path.write_text(json.dumps(manifest))
        result = self.run_command('create', self.source, self.dest)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = self.run_command('plan', self.source)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_setup_explicitly_excludes_references_during_migration(self):
        guide = (ROOT / '.claude/setup/README.md').read_text()
        for safeguard in ('Do not copy or recreate them in new or migrated workspaces',
                          'including during approved content migration',
                          'preserve existing owner files',
                          'Do not create a Cowork environment preference'):
            self.assertIn(safeguard, guide)

    def test_nonempty_destination_is_rejected_without_changes(self):
        self.dest.mkdir()
        (self.dest / 'owner.md').write_text('keep')
        result = self.run_command('create', self.source, self.dest)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.dest.iterdir()), [self.dest / 'owner.md'])

    def test_failed_copy_leaves_destination_retryable(self):
        spec = importlib.util.spec_from_file_location('cowork_workspace', SCRIPT)
        assert spec is not None and spec.loader is not None
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        manifest = helper.project(self.source)
        original = helper.source_file
        for existed in (False, True):
            with self.subTest(existing_empty=existed):
                destination = self.root / ('empty' if existed else 'new')
                if existed:
                    destination.mkdir()
                calls = 0

                def fail_second_read(*args):
                    nonlocal calls
                    calls += 1
                    if calls == 2:
                        raise OSError('simulated source read failure')
                    return original(*args)

                with (mock.patch.object(helper, 'source_file', side_effect=fail_second_read),
                      self.assertRaisesRegex(OSError, 'simulated source read failure')):
                    helper.create(self.source, destination, manifest)
                self.assertFalse(destination.exists() and any(destination.iterdir()))
                helper.create(self.source, destination, manifest)
                self.assertTrue((destination / 'MANIFEST.json').is_file())

    def test_manifest_traversal_and_symlink_escape_are_rejected(self):
        manifest_path = self.source / 'MANIFEST.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['files']['memory/../../outside.md'] = {'class': 'merge', 'mode': '644'}
        manifest_path.write_text(json.dumps(manifest))
        result = self.run_command('create', self.source, self.dest)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.dest.exists())
        del manifest['files']['memory/../../outside.md']
        manifest_path.write_text(json.dumps(manifest))
        external = self.root / 'outside.md'
        external.write_text('private')
        link = self.source / 'memory/schema.json'
        link.unlink()
        link.symlink_to(external)
        result = self.run_command('create', self.source, self.dest)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.dest.exists())

    def test_existing_parent_and_source_destination_overlap_are_rejected(self):
        result = self.run_command('create', self.source, self.source / 'nested')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.source / 'nested').exists())


class InstalledWorkspaceTests(unittest.TestCase):
    def test_real_user_workspace_audits_with_only_installed_packages(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workspace = root / 'user workspace'
            installed = root / 'Cowork installed'
            installed.mkdir()
            with zipfile.ZipFile(ROOT / '.claude/cowork/skills/core/personal-memory.skill') as package:
                package.extractall(installed)
            helper = installed / 'personal-memory'
            created = subprocess.run([sys.executable, str(SCRIPT), 'create', str(ROOT), str(workspace)],
                                     capture_output=True, text=True)
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            self.assertFalse((workspace / '.claude/skills').exists())
            for relative in ('START-HERE.md', 'memory/preferences/cowork-environment.md'):
                self.assertFalse((workspace / relative).exists(), relative)
            for relative in ('CLAUDE.md', 'memory/rules.md', 'memory/index.md'):
                text = (workspace / relative).read_text()
                self.assertNotIn('cowork-environment.md', text)
                self.assertNotIn('environment note', text)
            self.assertFalse(list(workspace.rglob('*.skill')))
            for relative in ('projects/README.md', 'memory/preferences/document-scaffolding.md'):
                self.assertNotIn('.claude/skills/', (workspace / relative).read_text())
            rules = (workspace / 'memory/rules.md').read_text()
            names = set(re.findall(r'skill `([^`]+)`', '\n'.join(line for line in rules.splitlines() if line.startswith('|'))))
            for name in names - {'personal-memory'}:
                package = ROOT / '.claude/cowork/skills/core' / (name + '.skill')
                with zipfile.ZipFile(package) as archive:
                    archive.extractall(installed)
            env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
            env['HOME'] = str(root / 'empty home')
            for script, args in [('indexes.py', []), ('hubs.py', []), ('gate.py', ['--memory', 'memory', 'audit'])]:
                result = subprocess.run([sys.executable, str(helper / script), *args], cwd=workspace,
                                        capture_output=True, text=True, env=env)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((helper / 'tasks.md').is_file())
            self.assertTrue((helper / 'task-templates.md').is_file())
            recovered = subprocess.run([sys.executable, str(helper / 'recovery.py'), '--root', str(workspace),
                                        'snapshot', 'memory/index.md'], cwd=workspace,
                                       capture_output=True, text=True, env=env)
            self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
            self.assertEqual(len(list((workspace / '.memory-recovery').glob('*/memory/index.md'))), 1)
            for args in [('init', '-q'), ('config', 'cowork.personalMemoryPath', str(helper)),
                         ('add', 'memory/index.md')]:
                subprocess.run(['git', *args], cwd=workspace, env=env, check=True, capture_output=True)
            checked = subprocess.run([sys.executable, str(workspace / '.githooks/pre-commit')],
                                     cwd=workspace, capture_output=True, text=True, env=env)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertFalse((workspace / '.claude/skills').exists())


if __name__ == '__main__':
    unittest.main()
