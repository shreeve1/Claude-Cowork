"""Shared procedures are structurally ready, not authorized by lint."""
import io
import json
from contextlib import redirect_stdout
import sys
from unittest.mock import patch
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_rules import workspace, audit as full_audit
from test_indexes import run_script, INDEXES, GATE
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import procedures

TODAY = date(2026, 10, 30)
BODY = """## Active memory
Trigger: review a change

### Prerequisites
A proposed change is available.

### Steps
1. Read the proposed change.

### Verify
Summarize findings before editing.

## Related
None.

## Notes
Owner tested the read-only steps.
"""


def write_procedure(mem, risk='read-only', approved='2026-10-01', verified='2026-10-01', body=BODY):
    path = mem / 'workflows/projects/review.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'---\ntype: procedure\ntitle: Review\nrisk: {risk}\napproved: {approved}\nverified: {verified}\n---\n{body}', encoding='utf-8')
    return path


class ProcedureTests(unittest.TestCase):
    def test_invalid_schema_topics_never_read_outside(self):
        for topic in ('../../outside', '/tmp/outside', 'C:/outside', '..\\outside', 42):
            with self.subTest(topic=topic), tempfile.TemporaryDirectory() as td:
                mem = workspace(td, [])
                config = json.loads((mem / 'schema.json').read_text())
                config['topics'] = [topic]
                (mem / 'schema.json').write_text(json.dumps(config))
                with patch.object(procedures.hubs, 'parse_frontmatter', side_effect=AssertionError('outside read')):
                    problems = procedures.audit(mem, TODAY)
                self.assertTrue(problems)
                self.assertIn('invalid workflow topic', problems[0])
                result = run_script(GATE, mem, 'audit')
                self.assertEqual(result.returncode, 1)
                self.assertNotIn('Traceback', result.stderr)

    def test_safe_symlinked_ancestor(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            real = base / 'real/project'
            real.mkdir(parents=True)
            mem = workspace(real, [])
            path = write_procedure(mem)
            run_script(INDEXES, mem)
            alias = base / 'alias'
            try:
                alias.symlink_to(base / 'real', target_is_directory=True)
            except OSError as exc:
                self.skipTest(str(exc))
            aliased = alias / 'project/memory'
            self.assertEqual(procedures.audit(aliased, TODAY), [])
            self.assertEqual(procedures.validate(aliased / path.relative_to(mem), TODAY), [])
            self.assertEqual(run_script(GATE, aliased, 'audit').returncode, 0)

    def test_selected_cli_ignores_unrelated_legacy_but_full_audit_fails(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, [])
            path = write_procedure(mem)
            legacy = path.with_name('legacy.md')
            legacy.write_text('---\ntype: procedure\n---\nIncomplete legacy procedure.')
            run_script(INDEXES, mem)
            selected = run_script(GATE, mem, 'procedures', 'memory/workflows/projects/review.md')
            self.assertEqual(selected.returncode, 0, selected.stdout + selected.stderr)
            self.assertEqual(run_script(GATE, mem, 'procedures').returncode, 1)
            self.assertEqual(run_script(GATE, mem, 'audit').returncode, 1)
            for target in ('memory/../outside.md', '/tmp/outside.md', 'memory/docs/x.md',
                           'memory/workflows/projects/legacy.md', 'memory/workflows/unknown/x.md'):
                result = run_script(GATE, mem, 'procedures', target)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertNotIn('Traceback', result.stderr)

    def test_compact_snapshots_exact_originals_and_stops_on_failure(self):
        import gate
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, [])
            originals = {}
            for name in gate.COMPACT_FILES:
                path = mem / name
                path.write_bytes(b'\xef\xbb\xbf| Name      | Value      |\r\n|---|---|\r\n| x      | y      |\r\n')
                originals[name] = path.read_bytes()
            result = run_script(GATE, mem, 'compact')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name, original in originals.items():
                copies = list((mem.parent / '.memory-recovery').rglob(name))
                self.assertEqual(len(copies), 1)
                self.assertEqual(copies[0].read_bytes(), original)
                self.assertNotEqual((mem / name).read_bytes(), original)
            (mem / 'index.md').write_bytes(originals['index.md'])
            with patch.object(gate.recovery, 'snapshot_memory', side_effect=OSError('denied')), \
                 patch.object(sys, 'argv', ['gate.py', '--memory', str(mem), 'compact']), \
                 redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as stopped:
                gate.main()
            self.assertEqual(stopped.exception.code, 1)
            self.assertEqual((mem / 'index.md').read_bytes(), originals['index.md'])

    def test_compact_stops_if_source_changes_before_snapshot(self):
        import gate
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, [])
            path = mem / 'index.md'
            path.write_text('| x      | y      |\n')
            real_snapshot = gate.recovery.snapshot_memory
            intervening = b'Owner intervening content.\n'
            def changed(memory_dir, name):
                path.write_bytes(intervening)
                return real_snapshot(memory_dir, name)
            with patch.object(gate.recovery, 'snapshot_memory', changed), \
                 patch.object(sys, 'argv', ['gate.py', '--memory', str(mem), 'compact']), \
                 redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as stopped:
                gate.main()
            self.assertEqual(stopped.exception.code, 1)
            self.assertEqual(path.read_bytes(), intervening)

    def test_selected_topic_named_workflows_cannot_hide_memory_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            real = root / 'real-memory'
            real.mkdir()
            from test_indexes import make_schema
            make_schema(real)
            data = json.loads((real / 'schema.json').read_text())
            data['topics'].append('workflows')
            (real / 'schema.json').write_text(json.dumps(data))
            path = write_procedure(real)
            nested = real / 'workflows/workflows/review.md'
            nested.parent.mkdir()
            nested.write_bytes(path.read_bytes())
            alias = root / 'memory'
            try:
                alias.symlink_to(real, target_is_directory=True)
            except OSError as exc:
                self.skipTest(str(exc))
            self.assertTrue(procedures.selected(alias, 'memory/workflows/workflows/review.md', TODAY))

    def test_blank_trigger_followed_by_prose_fails(self):
        with tempfile.TemporaryDirectory() as td:
            path = write_procedure(Path(td), body=BODY.replace('Trigger: review a change', 'Trigger:\nUnrelated explanation.'))
            self.assertTrue(procedures.validate(path, TODAY))

    def test_required_subsections_outside_active_memory_fail(self):
        misplaced = BODY.replace('## Active memory', '## Other').replace('## Notes', '## Active memory\nTrigger: review a change\n\n## Notes')
        state = BODY + '\n### Approval\nAsk now.\n### Recovery\nStop and escalate.\n'
        for body, risk in ((misplaced, 'read-only'), (state, 'changes-state')):
            with self.subTest(risk=risk), tempfile.TemporaryDirectory() as td:
                self.assertTrue(procedures.validate(write_procedure(Path(td), risk=risk, body=body), TODAY))

    def test_read_only_and_extra_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            path = write_procedure(Path(td))
            path.write_text(path.read_text().replace('type: procedure', 'extra: yes\ntype: procedure'))
            self.assertEqual(procedures.validate(path, TODAY), [])

    def test_missing_empty_sections_and_numbered_action(self):
        variants = [BODY.replace(section, '### Other') for section in
                    ('## Active memory', '### Prerequisites', '### Steps', '### Verify', '## Related', '## Notes')]
        variants += [BODY.replace('Trigger: review a change', 'Trigger:'), BODY.replace('1. Read the proposed change.', 'Read it.'),
                     BODY.replace('Summarize findings before editing.', ''), BODY.replace('None.', '')]
        for body in variants:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as td:
                path = write_procedure(Path(td), body=body)
                before = path.read_bytes()
                self.assertTrue(procedures.validate(path, TODAY))
                self.assertEqual(path.read_bytes(), before)

    def test_changes_state_requires_approval_recovery(self):
        with tempfile.TemporaryDirectory() as td:
            path = write_procedure(Path(td), risk='changes-state')
            self.assertTrue(procedures.validate(path, TODAY))
            path = write_procedure(Path(td), risk='changes-state', body=BODY.replace('## Related', '### Approval\nAsk now before publishing.\n\n### Recovery\nIrreversible; stop and escalate.\n\n## Related'))
            self.assertEqual(procedures.validate(path, TODAY), [])

    def test_dates_and_risk(self):
        for kwargs in ({'risk': 'maybe'}, {'approved': ''}, {'verified': ''}, {'approved': '2026-10-31'},
                       {'verified': '2026-02-30'}, {'approved': '20261001'}):
            with self.subTest(kwargs=kwargs), tempfile.TemporaryDirectory() as td:
                path = write_procedure(Path(td), **kwargs)
                self.assertTrue(procedures.validate(path, TODAY))

    def test_fenced_examples_do_not_count(self):
        with tempfile.TemporaryDirectory() as td:
            path = write_procedure(Path(td), body='```markdown\n' + BODY + '\n```')
            self.assertTrue(procedures.validate(path, TODAY))

    def test_bom_crlf(self):
        with tempfile.TemporaryDirectory() as td:
            path = write_procedure(Path(td))
            path.write_bytes(b'\xef\xbb\xbf' + path.read_bytes().replace(b'\n', b'\r\n'))
            self.assertEqual(procedures.validate(path, TODAY), [])

    def test_cli_and_full_audit_reject_legacy_without_writes(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, [])
            path = write_procedure(mem, approved='', verified='', body='## Active memory\nTrigger: test\n### Steps\n1. Do it.\n')
            run_script(INDEXES, mem)
            before = {p: p.read_bytes() for p in mem.rglob('*') if p.is_file()}
            for command in ('procedures', 'audit'):
                proc = run_script(GATE, mem, command)
                self.assertEqual(proc.returncode, 1, proc.stdout)
                self.assertIn('Procedure problems:', proc.stdout)
                self.assertIn('review.md', proc.stdout)
            self.assertEqual(before, {p: p.read_bytes() for p in mem.rglob('*') if p.is_file()})

    def test_full_audit_keeps_unrelated_findings(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, [])
            write_procedure(mem, body='Incomplete.')
            run_script(INDEXES, mem)
            note = mem / 'docs/unindexed.md'
            note.parent.mkdir()
            note.write_text('Unindexed ordinary note.')
            result = run_script(GATE, mem, 'audit')
            self.assertIn('Procedure problems:', result.stdout)
            self.assertIn('missing_from_index', result.stdout)

    def test_empty_and_ordinary_notes(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, [])
            path = write_procedure(mem)
            path.write_text('---\ntype: workflow\n---\nordinary note')
            self.assertEqual(procedures.audit(mem, TODAY), [])
            path.unlink()
            self.assertEqual(procedures.audit(mem, TODAY), [])
            self.assertEqual(run_script(GATE, mem, 'procedures').returncode, 0)

    def test_symlink_not_read(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, [])
            path = write_procedure(mem)
            outside = mem.parent / 'outside.md'
            outside.write_bytes(path.read_bytes())
            path.unlink()
            try:
                path.symlink_to(outside)
            except OSError as exc:
                self.skipTest(str(exc))
            self.assertTrue(procedures.audit(mem, TODAY))
            self.assertTrue(procedures.validate(path, TODAY))


if __name__ == '__main__':
    unittest.main()
