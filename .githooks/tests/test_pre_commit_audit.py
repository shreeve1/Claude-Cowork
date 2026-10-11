import importlib.machinery
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = Path(__file__).resolve().parents[1] / "pre-commit"
GATE_DIR = ROOT / ".claude/skills/personal-memory"
_loader = importlib.machinery.SourceFileLoader("pre_commit_audit", str(HOOK))
_spec = importlib.util.spec_from_loader("pre_commit_audit", _loader)
hook = importlib.util.module_from_spec(_spec)
_loader.exec_module(hook)


class AuditTriggerTests(unittest.TestCase):
    def test_trigger_paths(self):
        self.assertTrue(hook.needs_memory_audit(["memory/preferences/x.md"]))
        self.assertTrue(hook.needs_memory_audit([".claude/skills/antislop/SKILL.md"]))
        self.assertFalse(hook.needs_memory_audit(["reports/x.md", "tmp/y"]))

    def test_configured_client_folder_triggers_the_audit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "memory").mkdir()
            (root / "memory/schema.json").write_text('{"client_folder": "students"}', encoding="utf-8")
            old = Path.cwd()
            os.chdir(root)
            try:
                self.assertTrue(hook.needs_memory_audit(["students/ana/notes.md"]))
                self.assertFalse(hook.needs_memory_audit(["pupils/ana/notes.md"]))
            finally:
                os.chdir(old)


def clean_env(**extra):
    """Environment without the outer git's GIT_* variables (`git commit --only` sets GIT_INDEX_FILE), so a fixture repo never writes into the real commit's index."""
    return {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}, **extra}


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, env=clean_env())


class DeleteRunsAuditTests(unittest.TestCase):
    def run_delete_scenario(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            git(repo, "init", "-q")
            git(repo, "config", "user.email", "t@t")
            git(repo, "config", "user.name", "t")
            shutil.copytree(GATE_DIR, repo / ".claude/skills/personal-memory",
                            ignore=shutil.ignore_patterns("tests", "__pycache__"))
            mem = repo / "memory"
            (mem / "preferences").mkdir(parents=True)
            (mem / "schema.json").write_text(
                '{"client_subjects": [], "topics": [], "topic_dirs": [], "client_dirs": []}', encoding="utf-8")
            (mem / "preferences/p.md").write_text("---\ntitle: P\n---\nx\n", encoding="utf-8")
            (mem / "index.md").write_text("| [P](memory/preferences/p.md) | preference | x | 2026-10-10 |\n", encoding="utf-8")
            (mem / "rules.md").write_text(
                "| When | Lead | Also load | Note |\n|---|---|---|---|\n| Always | | `memory/preferences/p.md` | |\n",
                encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "base", "--no-verify")
            git(repo, "rm", "-q", "memory/preferences/p.md")
            return subprocess.run([sys.executable, str(HOOK)], cwd=repo, capture_output=True, text=True,
                                  env=clean_env(GIT_DIR=str(repo / ".git")))

    @unittest.skipUnless(GATE_DIR.is_dir(), "personal-memory skill not present")
    def test_deleting_a_rule_target_fails_the_commit(self):
        run = self.run_delete_scenario()
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn("memory/rules.md: memory/preferences/p.md not found", run.stderr)

    @unittest.skipUnless(GATE_DIR.is_dir(), "personal-memory skill not present")
    def test_outer_commit_index_is_never_written(self):
        """`git commit --only` runs the hook with GIT_INDEX_FILE set; the fixture repo must not write into it."""
        with tempfile.TemporaryDirectory() as outer_dir:
            outer = Path(outer_dir) / "index"
            with mock.patch.dict(os.environ, {"GIT_INDEX_FILE": str(outer)}):
                run = self.run_delete_scenario()
            self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
            self.assertFalse(outer.exists(), "fixture wrote into the outer commit's index")



if __name__ == "__main__":
    unittest.main()
