"""gate.py bloat warnings and the stale command."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_indexes import GATE, INDEXES, make_index, make_schema, run_script  # noqa: E402


def memory(td):
    mem = Path(td)
    make_index(mem)
    make_schema(mem)
    for d in ("workflows", "decisions"):
        (mem / d).mkdir()
    (mem / "decisions" / "memory").mkdir()
    return mem


def note(mem, rel, summary="Short.", body="- Rule.\n", status="promoted", updated="2026-10-01"):
    p = mem / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"---\ntitle: T\nsummary: {summary}\ntype: decision\nstatus: {status}\n"
                 f"updated: {updated}\n---\n\n## Decision\n\n{body}", encoding="utf-8")


def audit(mem):
    run_script(INDEXES, mem)
    return run_script(GATE, mem, "audit")


class BloatWarningTests(unittest.TestCase):
    def test_clean_note_has_no_warning(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            note(mem, "decisions/memory/decision-a.md", body="- Rule.\n\n## Notes\n\n- Changed 2026-10-10: why.\n")
            proc = audit(mem)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertNotIn("Warning:", proc.stdout)

    def test_oversize_note_warns_without_failing(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            note(mem, "decisions/memory/decision-a.md", body="x" * 7000 + "\n")
            proc = audit(mem)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("Warning: memory/decisions/memory/decision-a.md:", proc.stdout)
            self.assertIn("over 6144; trim or split", proc.stdout)

    def test_long_summary_warns(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            note(mem, "decisions/memory/decision-a.md", summary="s" * 161)
            proc = audit(mem)
            self.assertIn("Warning: memory/decisions/memory/decision-a.md: summary 161 chars, over 160", proc.stdout)

    def test_160_char_summary_is_fine(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            note(mem, "decisions/memory/decision-a.md", summary="s" * 160)
            self.assertNotIn("Warning:", audit(mem).stdout)

    def test_superseded_history_line_warns(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            note(mem, "decisions/memory/decision-a.md", body="- Rule.\n\n## Notes\n\n- Superseded 2026-10-01: old rule.\n")
            proc = audit(mem)
            self.assertIn("Warning: memory/decisions/memory/decision-a.md: history line; overwrite in place", proc.stdout)

    def test_superseded_status_warns_delete(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            note(mem, "decisions/memory/decision-a.md", status="superseded")
            proc = audit(mem)
            self.assertIn("Warning: memory/decisions/memory/decision-a.md: status superseded; delete the file", proc.stdout)

    def test_log_file_warns_retired(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            (mem / "log.md").write_text("# Memory Log\n", encoding="utf-8")
            proc = audit(mem)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("Warning: memory/log.md is retired", proc.stdout)

    def test_prose_starting_updated_is_not_history(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            note(mem, "decisions/memory/decision-a.md", body="Updated weekly by cron.\n- Amended per ticket.\n")
            self.assertNotIn("Warning:", audit(mem).stdout)

    def test_long_index_row_summary_warns(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            with (mem / "index.md").open("a", encoding="utf-8") as f:
                f.write(f"| [Long](memory/x.md) | doc | {'s' * 161} | 2026-10-10 |\n")
            proc = run_script(GATE, mem, "audit")
            self.assertIn("Warning: memory/index.md: row [Long](memory/x.md) summary over 160 chars", proc.stdout)

    def test_padded_index_warns_and_compact_removes_exactly_the_padding(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            (mem / "index.md").write_text(
                "# Memory Index\n\n## Promoted Memory\n\n"
                "| Page                                    | Type  | Summary    | Updated    |\n"
                "| --------------------------------------- | ----- | ---------- | ---------- |\n"
                "| [Workflow Index](memory/workflows/index.md) | index | Workflows. | 2026-10-07 |\n"
                "| [Decision Index](memory/decisions/index.md) | index | Decisions. | 2026-10-07 |\n\n"
                "## Client Hubs\n\n| Page | Type | Summary | Updated |\n|------|------|---------|---------|\n",
                encoding="utf-8")
            before = audit(mem)
            self.assertEqual(before.returncode, 0, before.stdout)
            self.assertIn("Warning: memory/index.md: table padding costs", before.stdout)
            run_script(GATE, mem, "compact")
            self.assertEqual(
                (mem / "index.md").read_text(encoding="utf-8"),
                "# Memory Index\n\n## Promoted Memory\n\n"
                "| Page | Type | Summary | Updated |\n"
                "|---|---|---|---|\n"
                "| [Workflow Index](memory/workflows/index.md) | index | Workflows. | 2026-10-07 |\n"
                "| [Decision Index](memory/decisions/index.md) | index | Decisions. | 2026-10-07 |\n\n"
                "## Client Hubs\n\n| Page | Type | Summary | Updated |\n|------|------|---------|---------|\n")
            after = audit(mem)
            self.assertEqual(after.returncode, 0, after.stdout)
            self.assertNotIn("table padding", after.stdout)

    def test_compact_leaves_template_index_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            before = (mem / "index.md").read_text(encoding="utf-8")
            run_script(GATE, mem, "compact")
            self.assertEqual((mem / "index.md").read_text(encoding="utf-8"), before)
            self.assertNotIn("table padding", audit(mem).stdout)

    def test_padded_rules_over_limit_points_to_compact_and_compact_fixes_it(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            pad = " " * 120
            rows = "".join(f"| When {i}{pad} | | `memory/glossary.md`{pad} | |\n" for i in range(30))
            (mem / "rules.md").write_text(f"# Rules\n\n| When{pad} | Lead | Also load | Note |\n|---|---|---|---|\n{rows}",
                                          encoding="utf-8")
            before = run_script(GATE, mem, "audit").stdout
            self.assertIn("memory/rules.md: table padding costs", before)
            self.assertIn("over 6144; run gate.py compact", before)
            run_script(GATE, mem, "compact")
            self.assertEqual((mem / "rules.md").read_text(encoding="utf-8").splitlines()[4],
                             "| When 0 | | `memory/glossary.md` | |")
            after = run_script(GATE, mem, "audit").stdout
            self.assertNotIn("memory/rules.md: table padding", after)
            self.assertNotIn("memory/rules.md: 8", after)

    def test_excluded_folders_are_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            for rel in ("raw/big.md", "candidates/big.md"):
                (mem / rel).parent.mkdir(parents=True, exist_ok=True)
                (mem / rel).write_text("x" * 7000, encoding="utf-8")
            self.assertNotIn("Warning:", audit(mem).stdout)

    def test_non_utf8_note_warns_without_failing(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            p = mem / "guides" / "bad.md"
            p.parent.mkdir()
            p.write_bytes(b"---\ntitle: T\n---\n\xff\xfe bad\n")
            with (mem / "index.md").open("a", encoding="utf-8") as f:
                f.write("| [Bad](memory/guides/bad.md) | guide | x | 2026-10-10 |\n")
            run_script(INDEXES, mem)
            proc = run_script(GATE, mem, "audit")
            self.assertIn("Warning: memory/guides/bad.md: not UTF-8", proc.stdout)
            self.assertNotIn("Traceback", proc.stderr)

    def test_non_utf8_decision_and_client_note_do_not_crash(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            (mem / "decisions" / "memory" / "decision-bad.md").write_bytes(
                b"---\ntitle: T\nsummary: s\nstatus: promoted\nupdated: 2026-10-01\n---\n\xff bad\n")
            client = mem / "clients" / "365" / "acme" / "n.md"
            client.parent.mkdir(parents=True)
            client.write_bytes(b"---\ntype: client-memory\nclient: acme\nsubject: 365\ntitle: T\n"
                               b"verified: 2026-10-01\nsource: x\n---\n\xff bad\n")
            run_script(INDEXES, mem)
            run_script(GATE.parent / "hubs.py", mem)
            with (mem / "index.md").open("a", encoding="utf-8") as f:
                f.write("| [acme hub](memory/clients/_hubs/acme.md) | client-hub | x | 2026-10-10 |\n")
            proc = run_script(GATE, mem, "audit")
            self.assertNotIn("Traceback", proc.stderr)
            self.assertIn("Warning: memory/decisions/memory/decision-bad.md: not UTF-8", proc.stdout)
            self.assertIn("Warning: memory/clients/365/acme/n.md: not UTF-8", proc.stdout)

    def test_crlf_and_bom_frontmatter_parse(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            p = mem / "decisions" / "memory" / "decision-crlf.md"
            p.write_bytes("\ufeff---\r\ntitle: T\r\nsummary: " .encode() + b"s" * 161 + b"\r\n---\r\nBody.\r\n")
            proc = audit(mem)
            self.assertIn("decision-crlf.md: summary 161 chars, over 160", proc.stdout)

    def test_dated_bullet_is_history(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            note(mem, "decisions/memory/decision-a.md", body="- Rule.\n- 2026-10-05: fixed it.\n")
            self.assertIn("decision-a.md: history line", audit(mem).stdout)

    def test_two_changed_lines_warn(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            note(mem, "decisions/memory/decision-a.md",
                 body="- Rule.\n\n## Notes\n\n- Changed 2026-10-01: a.\n- Changed 2026-10-05: b.\n")
            self.assertIn("decision-a.md: more than one Changed line", audit(mem).stdout)

    def test_missing_rules_with_preferences_warns(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            (mem / "preferences").mkdir()
            (mem / "preferences" / "p.md").write_text("---\ntitle: P\n---\nx\n", encoding="utf-8")
            with (mem / "index.md").open("a", encoding="utf-8") as f:
                f.write("| [P](memory/preferences/p.md) | preference | x | 2026-10-10 |\n")
            self.assertIn("Warning: memory/rules.md is missing", audit(mem).stdout)


class StaleTests(unittest.TestCase):
    def test_lists_only_notes_over_90_days(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            note(mem, "decisions/memory/decision-old.md", updated="2000-01-01")
            note(mem, "decisions/memory/decision-new.md", updated="2999-01-01")
            proc = run_script(GATE, mem, "stale")
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(proc.stdout, "2000-01-01 memory/decisions/memory/decision-old.md\n")

    def test_newest_of_updated_and_verified_wins(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            p = mem / "clients" / "365" / "acme" / "n.md"
            p.parent.mkdir(parents=True)
            p.write_text("---\nupdated: 2000-01-01\nverified: 2999-01-01\n---\nx\n", encoding="utf-8")
            self.assertEqual(run_script(GATE, mem, "stale").stdout, "")

    def test_malformed_date_is_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            note(mem, "decisions/memory/decision-bad.md", updated="2026-13-45")
            proc = run_script(GATE, mem, "stale")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout, "")


if __name__ == "__main__":
    unittest.main()
