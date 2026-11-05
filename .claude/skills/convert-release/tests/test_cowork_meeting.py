import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / '.claude/cowork/workspace.py'


class InstalledMeetingTests(unittest.TestCase):
    def test_list_runs_from_the_installed_skill_with_no_workspace_skill_tree(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            workspace = base / 'user workspace'
            installed = base / 'Cowork installed'
            installed.mkdir()
            with zipfile.ZipFile(ROOT / '.claude/cowork/skills/core/meeting.skill') as package:
                package.extractall(installed)
            created = subprocess.run([sys.executable, str(SCRIPT), 'create', str(ROOT), str(workspace)],
                                     capture_output=True, text=True)
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            self.assertFalse((workspace / '.claude/skills').exists())
            folder = base / 'Transcripts'
            folder.mkdir()
            transcript = folder / '2026-10-20 Supplier call.txt'
            transcript.write_text('Ana: we ship Friday.\nMe: I will send the PO.', encoding='utf-8')
            old = time.time() - 3600
            os.utime(transcript, (old, old))
            script = installed / 'meeting/scripts/meetings.py'

            def run(*args):
                result = subprocess.run([sys.executable, str(script), '--folder', str(folder), *args, 'list'],
                                        cwd=workspace, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return json.loads(result.stdout)

            for items in (run('--root', str(workspace)), run()):  # default root is the current folder
                self.assertEqual([i['name'] for i in items], [transcript.name])
                self.assertIsNone(items[0]['record'])
            # Records are searched under the workspace, not next to the installed script.
            record = workspace / 'notes/meetings/2026-10-20-supplier-call.md'
            record.parent.mkdir(parents=True)
            record.write_text(f"---\ntype: meeting-record\nsource: {transcript.name}\n"
                              f"transcript_hash: {run()[0]['transcript_hash']}\ndate: 2026-10-20 10:00\n---\n",
                              encoding='utf-8')
            self.assertEqual(run('--root', str(workspace))[0]['record'], 'notes/meetings/2026-10-20-supplier-call.md')
            self.assertEqual(run()[0]['record'], 'notes/meetings/2026-10-20-supplier-call.md')


if __name__ == '__main__':
    unittest.main()
