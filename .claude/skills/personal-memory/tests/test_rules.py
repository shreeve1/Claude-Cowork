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
