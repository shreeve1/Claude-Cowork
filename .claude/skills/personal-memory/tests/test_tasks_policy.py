"""Template and install contracts; agent behavior is verified with disposable probes."""
import re
import sys
import tempfile
from datetime import date
import unittest
from pathlib import Path

PM = Path(__file__).resolve().parents[1]
ROOT = PM.parents[2]


def markdown_blocks(path):
    text = path.read_text(encoding="utf-8")
    return re.findall(r"^```markdown\n(.*?)^```", text, re.M | re.S)


class TaskTemplateTests(unittest.TestCase):
    def test_changes_state_template_passes_real_procedure_validation(self):
        sys.path.insert(0, str(PM))
        from procedures import validate
        paths = [PM / "scaffold/TEMPLATES.md"]
        if (ROOT / "memory/TEMPLATES.md").is_file():
            paths.append(ROOT / "memory/TEMPLATES.md")
        for path in paths:
            with self.subTest(path=path):
                blocks = [block for block in markdown_blocks(path) if "risk: changes-state" in block]
                self.assertEqual(len(blocks), 1, "Copyable changes-state template missing")
                filled = blocks[0].replace("YYYY-MM-DD", "2026-10-30").replace("<topic>", "projects")
                with tempfile.TemporaryDirectory() as td:
                    fixture = Path(td) / "procedure.md"
                    fixture.write_text(filled, encoding="utf-8")
                    self.assertEqual(validate(fixture, today=date(2026, 10, 31)), [])

    def test_task_record_can_be_filled_without_design_documents(self):
        path = PM / "task-templates.md"
        self.assertTrue(path.is_file(), "Installed task template missing")
        blocks = markdown_blocks(path)
        record = blocks[0]
        for key in ("id", "title", "status", "created", "updated"):
            self.assertRegex(record, rf"(?m)^{key}: .+")
        for heading in ("Purpose", "Current position", "Next action", "References", "Progress", "Outcome", "Durable outputs"):
            self.assertIn("## " + heading, record)
        self.assertEqual(record.count("\n---"), 1)

    def test_empty_index_has_no_fictional_tasks(self):
        path = PM / "task-templates.md"
        self.assertTrue(path.is_file(), "Installed index template missing")
        index = markdown_blocks(path)[1]
        rows = [line for line in index.splitlines() if line.startswith("|")]
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows[0].split("|")), 8)

    def test_supporting_formats_are_installed_and_fences_parse(self):
        path = PM / "supporting-templates.md"
        self.assertTrue(path.is_file(), "Installed supporting templates missing")
        blocks = markdown_blocks(path)
        self.assertEqual(len(blocks), 2)
        self.assertIn("## Still needed", blocks[0])
        self.assertIn("## Findings:", blocks[1])
        self.assertIn("## Questions", blocks[1])

    def test_workspace_index_keeps_template_header(self):
        if not (ROOT / "CLAUDE.md").is_file():
            self.skipTest("Standalone skill install")
        path = ROOT / "tasks/index.md"
        self.assertTrue(path.is_file(), "Workspace task index missing")
        template = markdown_blocks(PM / "task-templates.md")[1]
        self.assertTrue(path.read_text(encoding="utf-8").startswith(template))

    def test_workspace_index_allows_real_task_rows(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "CLAUDE.md").write_text("# Workspace\n", encoding="utf-8")
            (root / "tasks").mkdir()
            template = markdown_blocks(PM / "task-templates.md")[1]
            (root / "tasks/index.md").write_text(
                template + "| [Real work](tasks/real.md) | Work | active | Check | | 2026-10-31 |\n",
                encoding="utf-8",
            )
            with patch.dict(globals(), ROOT=root):
                self.test_workspace_index_keeps_template_header()

    def test_task_recovery_is_excluded_from_git(self):
        if not (ROOT / ".gitignore").is_file():
            self.skipTest("Standalone skill install")
        import subprocess
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", ".task-recovery/probe/tasks/index.md"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_operations_are_packaged_with_copied_skill(self):
        # A self-contained copy must contain the targets reached by its reader.
        for name in ("tasks.md", "task-templates.md", "supporting-templates.md"):
            self.assertTrue((PM / name).is_file(), name)
        for path in (PM / "tasks.md", PM / "task-templates.md", PM / "supporting-templates.md"):
            text = path.read_text(encoding="utf-8")
            self.assertEqual(sum(line.startswith("```") for line in text.splitlines()) % 2, 0)
            instructions = re.sub(r"^```.*?^```", "", text, flags=re.M | re.S)
            for target in re.findall(r"\]\(([^)]+\.md)\)", instructions):
                self.assertTrue((path.parent / target).is_file(), target)


if __name__ == "__main__":
    unittest.main()
