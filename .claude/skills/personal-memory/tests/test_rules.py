"""gate.py audit over memory/rules.md: broken pointers and unreached preference files."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_indexes import GATE, INDEXES, make_index, make_schema, run_script  # noqa: E402

HEADER = "| When | Lead | Also load | Note |\n|---|---|---|---|\n"


def workspace(td, rows, skills=(), files=()):
    root = Path(td)
    mem = root / "memory"
    mem.mkdir()
    make_index(mem)
    make_schema(mem)
    for s in skills:
        (root / ".claude" / "skills" / s).mkdir(parents=True)
        (root / ".claude" / "skills" / s / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")
    for f, body in files:
        (root / f).parent.mkdir(parents=True, exist_ok=True)
        (root / f).write_text(body, encoding="utf-8")
    (mem / "rules.md").write_text("# Rules\n\n" + HEADER + "".join(r + "\n" for r in rows), encoding="utf-8")
    for d in ("workflows", "decisions"):
        (mem / d).mkdir()
    run_script(INDEXES, mem)
    return mem


def audit(mem):
    return subprocess.run([sys.executable, str(GATE), "--memory", str(mem), "audit"],
                          capture_output=True, text=True)


def index_row(path):
    return f"| [X]({path}) | preference | x | 2026-10-10 |\n"


class RulesAuditTests(unittest.TestCase):
    def test_valid_rules_pass(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Writing PowerShell | skill `powershell-expert` | `powershell/README.md` | |"],
                            skills=["powershell-expert"], files=[("powershell/README.md", "x")])
            proc = audit(mem)
            self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_placeholders_and_plain_words_are_not_paths(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Work on one client | | `memory/clients/_hubs/<short>.md` | |",
                                 "| Email | | | Fires on a plain `draft me an email`. |"])
            proc = audit(mem)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertNotIn("Rules problems:", proc.stdout)

    def test_missing_skill_fails(self):
        with tempfile.TemporaryDirectory() as td:
            mem = workspace(td, ["| Email | | skill `antislop` | |"])
            proc = audit(mem)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("- memory/rules.md: skill antislop not found", proc.stdout)

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
            self.assertIn("- memory/preferences/orphan.md: no row in memory/rules.md reaches it", proc.stdout)

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
            mem = workspace(td, ["| Writing for the owner | | `memory/preferences/guidelines.md` | |"],
                            files=[("memory/preferences/guidelines.md", "See `memory/preferences/notes.md`."),
                                   ("memory/preferences/notes.md", "x")])
            with (mem / "index.md").open("a", encoding="utf-8") as f:
                f.write(index_row("memory/preferences/guidelines.md") + index_row("memory/preferences/notes.md"))
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
