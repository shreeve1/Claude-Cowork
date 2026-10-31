"""Recovery must preserve exact previous bytes, including without Git."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import recovery


class RecoveryTests(unittest.TestCase):
    def source(self, td):
        root = Path(td)
        path = root / 'memory/docs/café.md'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'\xef\xbb\xbfPrevious\r\n\x00exact bytes\r\n')
        return root, path

    def test_exact_bytes_without_git_and_source_unchanged(self):
        with tempfile.TemporaryDirectory(prefix='recovery space ') as td:
            root, source = self.source(td)
            before = source.read_bytes()
            saved = recovery.snapshot(root, 'memory/docs/café.md')
            self.assertEqual(saved.read_bytes(), before)
            self.assertEqual(source.read_bytes(), before)
            self.assertTrue(saved.is_relative_to(root / '.memory-recovery'))
            self.assertFalse((root / '.git').exists())

    def test_safe_symlinked_ancestor(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root, source = self.source(base / 'real/project')
            alias = base / 'alias'
            try:
                alias.symlink_to(base / 'real', target_is_directory=True)
            except OSError as exc:
                self.skipTest(str(exc))
            saved = recovery.snapshot(alias / 'project', 'memory/docs/café.md')
            self.assertEqual(saved.read_bytes(), source.read_bytes())

    def test_unique_snapshots(self):
        with tempfile.TemporaryDirectory() as td:
            root, source = self.source(td)
            first = recovery.snapshot(root, 'memory/docs/café.md')
            second = recovery.snapshot(root, 'memory/docs/café.md')
            self.assertNotEqual(first, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_invalid_paths(self):
        for rel in ('/etc/passwd', 'C:/memory/file.md', 'memory\\docs\\x.md', 'memory/../x',
                    'memory//docs/x', 'memory/./docs/x', 'docs/x', 'memory/docs', 'memory/docs/absent.md'):
            with self.subTest(rel=rel), tempfile.TemporaryDirectory() as td:
                root, source = self.source(td)
                with self.assertRaises((ValueError, FileNotFoundError)):
                    recovery.snapshot(root, rel)
                self.assertTrue(source.exists())

    def test_symlink_boundaries(self):
        for location in ('source', 'parent', 'destination', 'root'):
            with self.subTest(location=location), tempfile.TemporaryDirectory() as td:
                root, source = self.source(td)
                outside = root / 'outside'
                outside.mkdir()
                try:
                    if location == 'source':
                        source.unlink()
                        (outside / 'x.md').write_text('external')
                        source.symlink_to(outside / 'x.md')
                    elif location == 'parent':
                        source.unlink()
                        source.parent.rmdir()
                        source.parent.symlink_to(outside, target_is_directory=True)
                    elif location == 'destination':
                        (root / '.memory-recovery').symlink_to(outside, target_is_directory=True)
                    else:
                        alias = root / 'alias'
                        alias.symlink_to(root, target_is_directory=True)
                        root = alias
                except OSError as exc:
                    self.skipTest(str(exc))
                with self.assertRaises(ValueError):
                    recovery.snapshot(root, 'memory/docs/café.md')

    def test_destination_checked_before_reading_source(self):
        with tempfile.TemporaryDirectory() as td:
            root, source = self.source(td)
            outside = root / 'outside'
            outside.mkdir()
            try:
                (root / '.memory-recovery').symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(str(exc))
            with patch.object(Path, 'read_bytes', side_effect=AssertionError('source read too early')):
                with self.assertRaises(ValueError):
                    recovery.snapshot(root, 'memory/docs/café.md')

    def test_copy_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root, source = self.source(td)
            original = source.read_bytes()
            real_open = Path.open
            def fail(path, *args, **kwargs):
                if args and args[0] == 'xb':
                    raise OSError('copy denied')
                return real_open(path, *args, **kwargs)
            with patch.object(Path, 'open', fail), self.assertRaises(OSError):
                recovery.snapshot(root, 'memory/docs/café.md')
            self.assertEqual(source.read_bytes(), original)

    def test_mismatched_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root, source = self.source(td)
            original = source.read_bytes()
            real_read = Path.read_bytes
            def wrong(path):
                return b'wrong' if '.memory-recovery' in path.parts else real_read(path)
            with patch.object(Path, 'read_bytes', wrong), self.assertRaises(OSError):
                recovery.snapshot(root, 'memory/docs/café.md')
            self.assertEqual(source.read_bytes(), original)

    def test_changed_source_during_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            root, source = self.source(td)
            real_read = Path.read_bytes
            reads = []
            def changed(path):
                if path == source:
                    reads.append(path)
                    if len(reads) == 2:
                        source.write_bytes(b'intervening edit')
                return real_read(path)
            with patch.object(Path, 'read_bytes', changed), self.assertRaises(OSError):
                recovery.snapshot(root, 'memory/docs/café.md')
            self.assertEqual(source.read_bytes(), b'intervening edit')
            saved = list((root / '.memory-recovery').rglob('café.md'))
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0].read_bytes(), b'\xef\xbb\xbfPrevious\r\n\x00exact bytes\r\n')

    def test_cli_spaces_unicode(self):
        with tempfile.TemporaryDirectory(prefix='space café ') as td:
            root, _ = self.source(td)
            run = subprocess.run([sys.executable, str(Path(recovery.__file__)), '--root', str(root),
                                  'snapshot', 'memory/docs/café.md'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn('Snapshot saved:', run.stdout)
            bad = subprocess.run([sys.executable, str(Path(recovery.__file__)), '--root', str(root),
                                  'snapshot', '../bad'], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            self.assertNotIn('Traceback', bad.stderr)

    def test_outside_recall_and_ignored(self):
        if not shutil.which('git'):
            self.skipTest('Git unavailable')
        with tempfile.TemporaryDirectory() as td:
            root, _ = self.source(td)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            repo = Path(__file__).resolve().parents[4]
            (root / '.gitignore').write_bytes((repo / '.gitignore').read_bytes())
            saved = recovery.snapshot(root, 'memory/docs/café.md')
            ignored = subprocess.run(['git', '-C', str(root), 'check-ignore', str(saved)], capture_output=True)
            self.assertEqual(ignored.returncode, 0)
            self.assertFalse(saved.is_relative_to(root / 'memory'))


if __name__ == '__main__':
    unittest.main()
