"""sweep.py retention rules and gate.py budgets for indexes and root context files."""

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_bloat import audit, memory  # noqa: E402
from test_indexes import GATE, INDEXES, run_script  # noqa: E402

SWEEP = Path(__file__).resolve().parents[1] / "sweep.py"


def make(root, rel, age_days, text="x"):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    t = time.time() - age_days * 86400
    os.utime(p, (t, t))
    return p


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t", *args],
        capture_output=True,
        text=True,
        check=True,
    )


def commit_all(root):
    if not (Path(root) / ".git").exists():
        git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", "fixture")


def sweep(root, *args, commit=True):
    if commit:
        commit_all(root)
    return subprocess.run(
        [sys.executable, str(SWEEP), "--root", str(root), *args], capture_output=True, text=True
    )


class GitSafetyTests(unittest.TestCase):
    def test_untracked_and_modified_files_are_never_deleted(self):
        with tempfile.TemporaryDirectory() as td:
            modified = make(td, ".sessions/modified.md", 200, "v1")
            clean = make(td, ".sessions/clean.md", 200)
            commit_all(td)
            modified.write_text("v2 edited after the commit", encoding="utf-8")
            os.utime(modified, (time.time() - 200 * 86400,) * 2)
            untracked = make(td, ".sessions/untracked.md", 200)
            proc = sweep(td, "--apply", commit=False)
            self.assertEqual(
                [modified.exists(), untracked.exists(), clean.exists()],
                [True, True, False],
                proc.stdout,
            )

    def test_outside_a_git_repo_nothing_is_deleted(self):
        with tempfile.TemporaryDirectory() as td:
            old = make(td, ".sessions/old.md", 200)
            proc = sweep(td, "--apply", commit=False)
            self.assertTrue(old.exists(), proc.stdout)
            self.assertIn("sweep: 0 files", proc.stdout)


class SweepTests(unittest.TestCase):
    def test_old_unreferenced_files_go_and_recent_ones_stay(self):
        with tempfile.TemporaryDirectory() as td:
            old_s = make(td, ".sessions/old.md", 120)
            new_s = make(td, ".sessions/new.md", 10)
            old_a = make(td, "artifacts/scratch/old.png", 120)
            new_a = make(td, "artifacts/scratch/new.png", 5)
            tmp_old = make(td, "tmp/old.txt", 400)
            proc = sweep(td, "--apply")
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertEqual([old_s.exists(), old_a.exists()], [False, False])
            self.assertEqual([new_s.exists(), new_a.exists(), tmp_old.exists()], [True, True, True])
            self.assertIn("sweep: 2 files", proc.stdout)

    def test_dry_run_deletes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            old = make(td, ".sessions/old.md", 120)
            proc = sweep(td)
            self.assertTrue(old.exists())
            self.assertIn("would delete .sessions/old.md", proc.stdout)

    def test_artifact_named_by_a_note_is_kept_by_file_or_by_topic_folder(self):
        with tempfile.TemporaryDirectory() as td:
            by_file = make(td, "artifacts/diagrams/flow.png", 200)
            by_topic = make(td, "artifacts/brand/palette/logo.svg", 200)
            unnamed = make(td, "artifacts/other/stale.csv", 200)
            make(
                td,
                "memory/preferences/p.md",
                1,
                "Palette: `artifacts/brand/palette/logo.svg`. Flow: artifacts/diagrams/flow.png\n",
            )
            make(td, "memory/preferences/q.md", 1, "The `artifacts/brand` folder holds the look.\n")
            sweep(td, "--apply")
            self.assertTrue(by_file.exists())
            self.assertTrue(by_topic.exists())
            self.assertFalse(unnamed.exists())

    def test_a_sibling_prefix_is_not_a_reference(self):
        with tempfile.TemporaryDirectory() as td:
            old = make(td, "artifacts/brand-old/x.png", 200)
            make(td, "memory/preferences/p.md", 1, "See artifacts/brand/ only.\n")
            sweep(td, "--apply")
            self.assertFalse(
                old.exists(), "a note naming artifacts/brand must not protect artifacts/brand-old"
            )

    def test_startday_runtime_state_and_other_folders_are_never_touched(self):
        with tempfile.TemporaryDirectory() as td:
            kept = [
                make(td, "artifacts/startday/ledger.jsonl", 400),
                make(td, "reports/old-report.md", 400),
                make(td, "memory/preferences/old.md", 400),
                make(td, "clients/acme/notes.md", 400),
            ]
            sweep(td, "--apply")
            self.assertEqual([p.exists() for p in kept], [True] * 4)

    def test_emptied_folders_are_removed_but_rule_folders_stay(self):
        with tempfile.TemporaryDirectory() as td:
            make(td, "artifacts/gone/deep/old.bin", 200)
            make(td, "artifacts/kept/new.bin", 1)
            sweep(td, "--apply")
            self.assertFalse((Path(td) / "artifacts/gone").exists())
            self.assertTrue((Path(td) / "artifacts/kept").exists())
            self.assertTrue((Path(td) / "artifacts").exists())

    def test_symlinks_are_not_followed(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside:
            target = make(outside, "precious.md", 400)
            link = Path(td) / "artifacts" / "link"
            link.parent.mkdir()
            link.symlink_to(target.parent)
            sweep(td, "--apply")
            self.assertTrue(target.exists())

    def test_missing_folders_are_fine(self):
        with tempfile.TemporaryDirectory() as td:
            proc = sweep(td, "--apply")
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("sweep: 0 files", proc.stdout)

    def test_a_note_naming_the_artifact_by_absolute_path_keeps_it(self):
        with tempfile.TemporaryDirectory() as td:
            old = make(td, "artifacts/brand/x.png", 200)
            make(td, "memory/preferences/p.md", 1, f"File: {td}/artifacts/brand/x.png.\n")
            sweep(td, "--apply")
            self.assertTrue(old.exists())

    def test_main_keeps_a_file_edited_between_listing_and_deleting(self):
        sys.path.insert(0, str(SWEEP.parent))
        import io

        import sweep as sw

        with tempfile.TemporaryDirectory() as td:
            old = make(td, ".sessions/old.md", 200, "committed text")
            commit_all(td)
            real = sw.candidates

            def list_then_edit(root, now):
                listed = real(root, now)
                old.write_text("edited by another session", encoding="utf-8")
                return listed

            sw.candidates = list_then_edit
            argv, out = sys.argv, io.StringIO()
            sys.argv, stdout = ["sweep.py", "--root", td, "--apply"], sys.stdout
            sys.stdout = out
            try:
                sw.main()
            finally:
                sw.candidates, sys.argv, sys.stdout = real, argv, stdout
            self.assertEqual(
                old.read_text(encoding="utf-8"), "edited by another session", out.getvalue()
            )
            self.assertIn("skipped .sessions/old.md", out.getvalue())
            self.assertIn("sweep: 0 files", out.getvalue())

    def test_a_note_naming_a_longer_sibling_does_not_protect_this_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            old = make(td, "artifacts/brand/x.png", 200)
            make(td, "memory/preferences/p.md", 1, "See artifacts/brand-old/y.png only.\n")
            sweep(td, "--apply")
            self.assertFalse(old.exists(), "'artifacts/brand-old/y.png' is not 'artifacts/brand'")

    def test_a_symlinked_rule_folder_is_not_swept_or_pruned(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside:
            target = make(outside, "sub/old.md", 400)
            empty = Path(outside) / "empty-sub"
            empty.mkdir()
            (Path(td) / ".sessions").symlink_to(outside)
            sweep(td, "--apply")
            self.assertTrue(target.exists())
            self.assertTrue(empty.exists())

    def test_a_root_below_the_repository_top_deletes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            work = Path(td) / "workspace"
            old = make(work, ".sessions/old.md", 200)
            commit_all(td)
            proc = sweep(work, "--apply", commit=False)
            self.assertTrue(old.exists(), proc.stdout)

    def test_renamed_files_are_kept(self):
        with tempfile.TemporaryDirectory() as td:
            make(td, ".sessions/before.md", 200, "same text")
            commit_all(td)
            git(td, "mv", ".sessions/before.md", ".sessions/after.md")
            os.utime(Path(td) / ".sessions/after.md", (time.time() - 200 * 86400,) * 2)
            proc = sweep(td, "--apply", commit=False)
            self.assertTrue((Path(td) / ".sessions/after.md").exists(), proc.stdout)

    def test_a_file_edited_after_listing_survives_with_its_new_text(self):
        sys.path.insert(0, str(SWEEP.parent))
        import sweep as sw

        with tempfile.TemporaryDirectory() as td:
            old = make(td, ".sessions/old.md", 200, "committed text")
            commit_all(td)
            root = Path(td).resolve()
            self.assertEqual([c[0] for c in sw.candidates(root, time.time())], [".sessions/old.md"])
            old.write_text("edited by another session", encoding="utf-8")
            deleted, note = sw.delete_if_restorable(root, ".sessions/old.md")
            self.assertFalse(deleted, note)
            self.assertEqual(old.read_text(encoding="utf-8"), "edited by another session")
            self.assertEqual([p.name for p in old.parent.iterdir()], ["old.md"])

    def test_an_edit_the_clean_filter_would_normalise_away_is_not_deleted(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td, ".gitattributes").write_text("*.md text eol=lf\n", encoding="utf-8")
            old = Path(td) / ".sessions" / "old.md"
            old.parent.mkdir()
            old.write_bytes(b"line one\nline two\n")
            os.utime(old, (time.time() - 200 * 86400,) * 2)
            commit_all(td)
            old.write_bytes(b"line one\r\nline two\r\n")
            os.utime(old, (time.time() - 200 * 86400,) * 2)
            proc = sweep(td, "--apply", commit=False)
            self.assertEqual(old.read_bytes(), b"line one\r\nline two\r\n", proc.stdout)

    def test_a_modified_file_whose_name_was_recreated_keeps_both_versions(self):
        sys.path.insert(0, str(SWEEP.parent))
        import sweep as sw

        with tempfile.TemporaryDirectory() as td:
            old = make(td, ".sessions/old.md", 200, "committed text")
            commit_all(td)
            root = Path(td).resolve()
            old.write_text("edited before the sweep", encoding="utf-8")
            real = sw.matches_head

            def recreate_then_check(r, rel, path=None):
                (root / rel).write_text("a writer recreated the name", encoding="utf-8")
                return real(r, rel, path)

            sw.matches_head = recreate_then_check
            try:
                deleted, note = sw.delete_if_restorable(root, ".sessions/old.md")
            finally:
                sw.matches_head = real
            self.assertFalse(deleted)
            texts = sorted(p.read_text(encoding="utf-8") for p in old.parent.iterdir())
            self.assertEqual(texts, ["a writer recreated the name", "edited before the sweep"])
            self.assertIn(".sweep-", note)

    def test_an_assume_unchanged_edit_is_not_deleted(self):
        with tempfile.TemporaryDirectory() as td:
            old = make(td, ".sessions/old.md", 200, "committed text")
            commit_all(td)
            git(td, "update-index", "--assume-unchanged", ".sessions/old.md")
            old.write_text("uncommitted edit git cannot see", encoding="utf-8")
            os.utime(old, (time.time() - 200 * 86400,) * 2)
            proc = sweep(td, "--apply", commit=False)
            self.assertEqual(
                old.read_text(encoding="utf-8"), "uncommitted edit git cannot see", proc.stdout
            )

    def test_a_write_landing_after_the_move_aside_is_never_lost(self):
        sys.path.insert(0, str(SWEEP.parent))
        import sweep as sw

        with tempfile.TemporaryDirectory() as td:
            old = make(td, ".sessions/old.md", 200, "committed text")
            commit_all(td)
            root = Path(td).resolve()
            real = sw.matches_head

            def writer_wins(r, rel, path=None):
                (root / rel).write_text("new file created while sweeping", encoding="utf-8")
                return real(r, rel, path)

            sw.matches_head = writer_wins
            try:
                deleted, note = sw.delete_if_restorable(root, ".sessions/old.md")
            finally:
                sw.matches_head = real
            self.assertTrue(deleted, note)
            self.assertEqual(old.read_text(encoding="utf-8"), "new file created while sweeping")

    def test_a_url_encoded_reference_keeps_the_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            old = make(td, "artifacts/client diagrams/flow.png", 200)
            make(
                td,
                "memory/preferences/p.md",
                1,
                "![flow](../artifacts/client%20diagrams/flow.png)\n",
            )
            sweep(td, "--apply")
            self.assertTrue(old.exists())

    def test_an_unreadable_note_folder_stops_the_sweep_without_deleting(self):
        if os.geteuid() == 0:
            self.skipTest("root ignores permissions")
        with tempfile.TemporaryDirectory() as td:
            old = make(td, "artifacts/topic/old.png", 200)
            hidden = make(td, "memory/locked/note.md", 1, "artifacts/topic/old.png\n")
            commit_all(td)
            hidden.parent.chmod(0)
            try:
                proc = sweep(td, "--apply", commit=False)
            finally:
                hidden.parent.chmod(0o755)
            self.assertTrue(old.exists(), proc.stdout)
            self.assertEqual(proc.returncode, 2, proc.stdout)

    def test_a_workspace_root_elsewhere_than_the_memory_parent_is_checked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "notes" / "personal").mkdir(parents=True)
            mem = memory(root / "notes" / "personal")
            (root / "CLAUDE.md").write_text("a" * 16385, encoding="utf-8")
            run_script(INDEXES, mem)
            out = run_script(GATE, mem, "--root", str(root), "audit").stdout
            self.assertRegex(out, r"Warning: CLAUDE\.md: 16385 bytes, over 16384")


class BudgetTests(unittest.TestCase):
    def test_oversize_index_warns(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            (mem / "index.md").write_text(
                (mem / "index.md").read_text(encoding="utf-8") + "\n" + "x" * 10300,
                encoding="utf-8",
            )
            self.assertRegex(audit(mem).stdout, r"Warning: memory/index\.md: \d+ bytes, over 10240")

    def test_index_under_budget_is_quiet(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertNotIn("over 10240", audit(memory(td)).stdout)

    def test_root_context_files_warn_only_over_their_own_limit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "memory").mkdir()
            mem = memory(root / "memory")
            (root / "CLAUDE.md").write_text("a" * 16385, encoding="utf-8")
            (root / "CONTEXT.md").write_text("c" * 20000, encoding="utf-8")
            out = audit(mem).stdout
            self.assertRegex(out, r"Warning: CLAUDE\.md: 16385 bytes, over 16384")
            self.assertNotIn("CONTEXT.md", out)

    def test_padded_glossary_is_compacted_without_touching_prose(self):
        with tempfile.TemporaryDirectory() as td:
            mem = memory(td)
            (mem / "glossary.md").write_text(
                "## Clients\n| Short   | Halo client ID |\n| ------- | -------------- |\n| acme    | 1              |\n\n"
                "Note   with   spaces.\n",
                encoding="utf-8",
            )
            run_script(GATE, mem, "compact")
            self.assertEqual(
                (mem / "glossary.md").read_text(encoding="utf-8"),
                "## Clients\n| Short | Halo client ID |\n|---|---|\n| acme | 1 |\n\nNote   with   spaces.\n",
            )


if __name__ == "__main__":
    unittest.main()
