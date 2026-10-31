"""gate.py audit over memory/rules.md: broken pointers and unreached preference files."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_indexes import (  # noqa: E402
    GATE,
    HUBS,
    INDEXES,
    SKILL_DIR,
    make_index,
    make_schema,
    run_script,
)

HEADER = "| When | Lead | Also load | Note |\n|---|---|---|---|\n"


def workspace(td, rows, skills=(), files=()):
    root = Path(td)
    mem = root / "memory"
    mem.mkdir()
    make_index(mem)
    make_schema(mem)
    for s in skills:
        (root / ".claude" / "skills" / s).mkdir(parents=True)
        (root / ".claude" / "skills" / s / "SKILL.md").write_text(
            "---\nname: x\n---\n", encoding="utf-8"
        )
    for f, body in files:
        (root / f).parent.mkdir(parents=True, exist_ok=True)
        (root / f).write_text(body, encoding="utf-8")
    (mem / "rules.md").write_text(
        "# Rules\n\n" + HEADER + "".join(r + "\n" for r in rows), encoding="utf-8"
    )
    for d in ("workflows", "decisions"):
        (mem / d).mkdir()
    run_script(INDEXES, mem)
    return mem


def audit(mem, home=None):
    """Run with an empty HOME so installed global skills do not leak in."""
    if home is None:
        home = mem.parent / "home"
        home.mkdir(exist_ok=True)
    return subprocess.run(
        [sys.executable, str(GATE), "--memory", str(mem), "audit"],
        capture_output=True,
        text=True,
        env={**os.environ, "HOME": str(home)},
    )


def global_skill(home, name):
    (home / ".claude" / "skills" / name).mkdir(parents=True)
    (home / ".claude" / "skills" / name / "SKILL.md").write_text(
        "---\nname: x\n---\n", encoding="utf-8"
    )


def copied_gate_audit(td, mem):
    root = Path(td)
    skill = root / "skills" / "personal-memory"
    skill.mkdir(parents=True)
    for script in SKILL_DIR.glob("*.py"):
        shutil.copy2(script, skill / script.name)
    sibling = root / "skills" / "sibling"
    sibling.mkdir()
    (sibling / "SKILL.md").write_text("---\nname: sibling\n---\n", encoding="utf-8")
    home = root / "empty-home"
    home.mkdir()
    return subprocess.run(
        [sys.executable, str(skill / "gate.py"), "--memory", str(mem), "audit"],
        capture_output=True,
        text=True,
        env={**os.environ, "HOME": str(home)},
        cwd=td,
    )


def index_row(path):
    return f"| [X]({path}) | preference | x | 2026-10-10 |\n"


class TaskIndexPointerTests(unittest.TestCase):
    def test_optional_task_index_absent_passes_without_writes(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Always | | `tasks/index.md` | |"])
            proc = audit(mem)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertFalse((mem.parent / "tasks").exists())

    def test_task_index_existing_passes(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Always | | `tasks/index.md` | |"], files=[("tasks/index.md", "# Active tasks\n")])
            self.assertEqual(audit(mem).returncode, 0)

    def test_task_index_symlink_escape_fails(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside:
            mem = workspace(td, ["| Always | | `tasks/index.md` | |"])
            external = Path(outside) / "index.md"
            external.write_text("outside", encoding="utf-8")
            (mem.parent / "tasks").mkdir()
            try:
                (mem.parent / "tasks/index.md").symlink_to(external)
            except OSError:
                self.skipTest("Symlinks unavailable")
            proc = audit(mem)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("unsafe task index", proc.stdout)
            self.assertEqual(external.read_text(), "outside")

    def test_dangling_task_directory_escape_fails(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside:
            mem = workspace(td, ["| Always | | `tasks/index.md` | |"])
            try:
                (mem.parent / "tasks").symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("Symlinks unavailable")
            proc = audit(mem)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("unsafe task index", proc.stdout)

    def test_task_parent_file_fails_without_changes(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Always | | `tasks/index.md` | |"])
            parent = mem.parent / "tasks"
            parent.write_bytes(b"Owner content, not a directory.\n")
            proc = audit(mem)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("unsafe task index", proc.stdout)
            self.assertEqual(parent.read_bytes(), b"Owner content, not a directory.\n")

    def test_dangling_contained_task_parent_fails(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Always | | `tasks/index.md` | |"])
            parent = mem.parent / "tasks"
            try:
                parent.symlink_to(mem.parent / "missing", target_is_directory=True)
            except OSError:
                self.skipTest("Symlinks unavailable")
            proc = audit(mem)
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("unsafe task index", proc.stdout)
            self.assertTrue(parent.is_symlink())
            self.assertFalse((mem.parent / "missing").exists())

    def test_existing_task_directory_without_index_passes(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Always | | `tasks/index.md` | |"])
            (mem.parent / "tasks").mkdir()
            proc = audit(mem)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertFalse((mem.parent / "tasks/index.md").exists())

    def test_task_index_directory_fails(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Always | | `tasks/index.md` | |"])
            (mem.parent / "tasks/index.md").mkdir(parents=True)
            self.assertNotEqual(audit(mem).returncode, 0)

    def test_other_missing_pointer_still_fails(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Always | | `tasks/other.md` | |"])
            proc = audit(mem)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("tasks/other.md not found", proc.stdout)


class ProcedureLeadTests(unittest.TestCase):
    def fixture(self, td, lead, kind="procedure", name="review.md"):
        rel = f"memory/workflows/projects/{name}"
        mem = workspace(td, [f"| Review | {lead} | | |"])
        path = mem.parent / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\ntitle: Review\ntype: {kind}\nrisk: read-only\napproved: 2026-10-01\nverified: 2026-10-01\n---\n"
            "## Active memory\nTrigger: review\n### Prerequisites\nChange available.\n"
            "### Steps\n1. Read change.\n### Verify\nReport findings.\n## Related\nNone.\n## Notes\nTested.\n",
            encoding="utf-8",
        )
        run_script(INDEXES, mem)
        return mem, path

    def test_procedure_lead_passes(self):
        with tempfile.TemporaryDirectory() as td:
            mem, _ = self.fixture(td, 'procedure `memory/workflows/projects/review.md`')
            result = audit(mem)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_multiple_leads_fail(self):
        with tempfile.TemporaryDirectory() as td:
            mem, _ = self.fixture(td, 'procedure `memory/workflows/projects/review.md`, procedure `memory/workflows/projects/review.md`')
            result = audit(mem)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn('memory/rules.md:', result.stdout)

    def test_procedure_lead_rejects_nonprocedure(self):
        with tempfile.TemporaryDirectory() as td:
            mem, _ = self.fixture(td, 'procedure `memory/workflows/projects/review.md`', kind="workflow")
            self.assertEqual(audit(mem).returncode, 1)

    def test_procedure_lead_rejects_escape(self):
        for target in ('/tmp/outside.md', 'C:/outside.md', 'memory/../outside.md',
                       'memory\\workflows\\projects\\review.md', 'memory/docs/review.md',
                       'memory/workflows/unknown/review.md'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as td:
                mem, _ = self.fixture(td, f'procedure `{target}`')
                result = audit(mem)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('memory/rules.md:', result.stdout)

    def test_procedure_lead_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as td:
            mem, path = self.fixture(td, 'procedure `memory/workflows/projects/review.md`')
            outside = Path(td) / 'outside.md'
            outside.write_bytes(path.read_bytes())
            path.unlink()
            try:
                path.symlink_to(outside)
            except OSError as exc:
                self.skipTest(str(exc))
            self.assertEqual(audit(mem).returncode, 1)

    def test_procedure_lead_rejects_symlink_loop(self):
        with tempfile.TemporaryDirectory() as td:
            mem, path = self.fixture(td, 'procedure `memory/workflows/projects/review.md`')
            path.unlink()
            try:
                path.symlink_to(path.name)
            except OSError as exc:
                self.skipTest(str(exc))
            result = audit(mem)
            self.assertEqual(result.returncode, 1)
            self.assertTrue('invalid procedure target' in result.stdout or 'symlink' in result.stdout)
            self.assertNotIn('Traceback', result.stderr)

    def test_procedure_lead_accepts_unicode_path(self):
        with tempfile.TemporaryDirectory(prefix='memory space ') as td:
            mem, _ = self.fixture(td, 'procedure `memory/workflows/projects/café.md`', name='café.md')
            result = audit(mem)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_unsupported_lead_fails(self):
        with tempfile.TemporaryDirectory() as td:
            mem, _ = self.fixture(td, 'run `memory/workflows/projects/review.md`')
            self.assertEqual(audit(mem).returncode, 1)


class RulesAuditTests(unittest.TestCase):
    def test_global_skill_passes(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Email | | skill `only-in-home` | |"])
            home = Path(td) / "home"
            global_skill(home, "only-in-home")
            proc = audit(mem, home)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertNotIn("skill only-in-home not found", proc.stdout)

    def test_skill_missing_locally_and_globally_fails(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Email | | skill `missing-test-skill` | |"])
            home = Path(td) / "home"
            global_skill(home, "other-skill")
            proc = audit(mem, home)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("memory/rules.md: skill missing-test-skill not found", proc.stdout)

    def test_runs_outside_git_repo(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(
                td,
                ["| Shorthand name | | `memory/glossary.md` | |"],
                files=[("memory/glossary.md", "# Glossary\n")],
            )
            self.assertFalse((Path(td) / ".git").exists())
            env = {**os.environ, "GIT_CEILING_DIRECTORIES": td}
            for script in (INDEXES, HUBS, GATE):
                args = ["audit"] if script == GATE else []
                proc = subprocess.run(
                    [sys.executable, str(script), "--memory", str(mem), *args],
                    capture_output=True,
                    text=True,
                    env=env,
                    cwd=td,
                )
                self.assertEqual(proc.returncode, 0, f"{script.name}: {proc.stdout}{proc.stderr}")

    def test_skill_next_to_script_passes(self):
        with tempfile.TemporaryDirectory(prefix="memory skills ") as td:
            mem = workspace(td, ["| Email | | skill `sibling` | |"])
            proc = copied_gate_audit(td, mem)
            self.assertFalse((Path(td) / ".claude").exists())
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_valid_rules_pass(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(
                td,
                ["| Writing PowerShell | skill `powershell-expert` | `powershell/README.md` | |"],
                skills=["powershell-expert"],
                files=[("powershell/README.md", "x")],
            )
            proc = audit(mem)
            self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_placeholders_and_plain_words_are_not_paths(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(
                td,
                [
                    "| Work on one client | | `memory/clients/_hubs/<short>.md` | |",
                    "| Email | | | Fires on a plain `draft me an email`. |",
                ],
            )
            proc = audit(mem)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertNotIn("Rules problems:", proc.stdout)

    def test_missing_skill_fails(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Email | | skill `missing-test-skill` | |"])
            proc = audit(mem)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("- memory/rules.md: skill missing-test-skill not found", proc.stdout)

    def test_missing_path_fails(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Email | | `memory/email/tone.md` | |"])
            proc = audit(mem)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("- memory/rules.md: memory/email/tone.md not found", proc.stdout)

    def test_unreached_preference_fails(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Always | | | |"], files=[("memory/preferences/orphan.md", "x")])
            with (mem / "index.md").open("a", encoding="utf-8") as f:
                f.write(index_row("memory/preferences/orphan.md"))
            proc = audit(mem)
            self.assertEqual(proc.returncode, 1)
            self.assertIn(
                "- memory/preferences/orphan.md: no row in memory/rules.md reaches it", proc.stdout
            )

    def test_unreached_email_file_fails(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Always | | | |"], files=[("memory/email/x.md", "x")])
            with (mem / "index.md").open("a", encoding="utf-8") as f:
                f.write(index_row("memory/email/x.md"))
            proc = audit(mem)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("- memory/email/x.md: no row in memory/rules.md reaches it", proc.stdout)

    def test_preference_reached_through_named_file_passes(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(
                td,
                ["| Writing for the owner | | `memory/preferences/guidelines.md` | |"],
                files=[
                    ("memory/preferences/guidelines.md", "See `memory/preferences/notes.md`."),
                    ("memory/preferences/notes.md", "x"),
                ],
            )
            with (mem / "index.md").open("a", encoding="utf-8") as f:
                f.write(
                    index_row("memory/preferences/guidelines.md")
                    + index_row("memory/preferences/notes.md")
                )
            proc = audit(mem)
            self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_no_rules_file_skips_check(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, [], files=[("memory/preferences/orphan.md", "x")])
            (mem / "rules.md").unlink()
            with (mem / "index.md").open("a", encoding="utf-8") as f:
                f.write(index_row("memory/preferences/orphan.md"))
            proc = audit(mem)
            self.assertEqual(proc.returncode, 0, proc.stdout)


if __name__ == "__main__":
    unittest.main()
