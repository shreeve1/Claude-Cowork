"""Template and install contracts; agent behavior is verified with disposable probes."""
import re
import sys
import tempfile
import unittest
from datetime import date
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
        proposals = [block for block in blocks if block.startswith("# Proposal:")]
        research = [block for block in blocks if block.startswith("# Research:")]
        self.assertEqual(len(proposals), 1)
        self.assertEqual(len(research), 1)
        self.assertIn("## Still needed", proposals[0])
        self.assertIn("## Findings:", research[0])
        self.assertIn("## Questions", research[0])

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

    def test_distributed_tasks_keep_one_central_index_and_safe_homes(self):
        policy = (PM / "tasks.md").read_text(encoding="utf-8")
        for home in ("projects/<subject>/tasks/", "clients/<client>/tasks/", "tasks/index.md"):
            self.assertIn(home, policy)
        for rule in ("approved task homes", "workspace-wide", "same task home", "escaping symlinks",
                     "legacy", "missing or stale", "never authorizes execution", "Search recursively",
                     "verified move", "update affected README"):
            self.assertIn(rule, policy)
        self.assertNotIn("Work only in the current workspace's `tasks/` and `tasks/archive/`.", policy)

    def test_distributed_lifecycle_safeguards_are_explicit(self):
        policy = (PM / "tasks.md").read_text(encoding="utf-8")
        scope = policy.split("## Scope and permission", 1)[1].split("## Start", 1)[0]
        for safeguard in ("including archive collision subfolders",
                          "check each directory's containment before descending",
                          "an index link cannot approve a new home",
                          "never follow an unverified link during discovery"):
            self.assertIn(safeguard, scope)
        start = policy.split("## Start", 1)[1].split("## Lookup", 1)[0]
        self.assertIn("must be workspace-wide unique across all approved task homes and archives", start)
        reopen = policy.split("## Continue", 1)[1].split("## Review", 1)[0]
        for safeguard in ("Reopening is a verified move, not a second live copy",
                          "preserve prior bytes in task recovery",
                          "update affected README and proposal links under the same recovery checks",
                          "Verify the old archive path is gone before adding the active row"):
            self.assertIn(safeguard, reopen)
        recovery = policy.split("## Recovery and failures", 1)[1]
        self.assertIn("handwritten task index, task-linked README or proposal", recovery)
        self.assertIn("no automatic pruning, retention expiry or deletion outside an authorized, verified move", recovery)

    def test_distributed_templates_support_project_and_client_records(self):
        templates = (PM / "task-templates.md").read_text(encoding="utf-8")
        for target in ("projects/<subject>/tasks/<task-name>.md", "clients/<client>/tasks/<task-name>.md",
                       "<workspace-relative-task-path>"):
            self.assertIn(target, templates)

    def test_distributed_adaptation_preserves_owner_layout(self):
        path = ROOT / ".claude/skills/memory-setup/tracking-model.md"
        if not path.is_file():
            self.skipTest("Standalone skill install has no setup guide")
        tracking = path.read_text(encoding="utf-8")
        self.assertIn("one root `tasks/index.md`", tracking)
        adaptation = (ROOT / ".claude/setup/ADAPTING.md").read_text(encoding="utf-8")
        self.assertIn("preserve the owner's existing organization", adaptation)
        self.assertIn("tasks/index.md", adaptation)
        self.assertIn("Do not move existing tasks", adaptation)

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
