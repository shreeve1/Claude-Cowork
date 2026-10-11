"""Tests for the edition pre-push hook: pushes touching memory/ or clients/ are refused.

Each test builds a real temp repo plus a local bare remote, installs the hook via
core.hooksPath, and pushes with git so the hook runs exactly as it will for an owner.
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "pre-push"


def git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


class PrePushTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.bare = base / "remote.git"
        self.repo = base / "repo"
        git(["init", "--bare", str(self.bare)], base)
        git(["init", "-b", "main", str(self.repo)], base)
        hooks = base / "hooks"
        hooks.mkdir()
        shutil.copy2(HOOK, hooks / "pre-push")
        os.chmod(hooks / "pre-push", 0o755)
        git(["config", "core.hooksPath", str(hooks)], self.repo)
        git(["config", "user.name", "Test"], self.repo)
        git(["config", "user.email", "test@example.com"], self.repo)

    def tearDown(self):
        self.tmp.cleanup()

    def commit_file(self, relpath):
        p = self.repo / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("content\n")
        git(["add", relpath], self.repo)
        r = git(["commit", "-m", f"add {relpath}"], self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)

    def push(self):
        return git(["push", "-u", str(self.bare), "main"], self.repo)

    def test_push_touching_memory_is_refused(self):
        self.commit_file("memory/x.md")
        r = self.push()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("pre-push", r.stderr)

    def test_push_touching_clients_is_refused(self):
        self.commit_file("clients/exampleco/notes.md")
        r = self.push()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("pre-push", r.stderr)

    def test_push_touching_only_src_is_allowed(self):
        self.commit_file("src/a.txt")
        r = self.push()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("pre-push", r.stderr)

    def test_non_ascii_memory_filename_is_refused(self):
        self.commit_file("memory/clients/caf\u00e9.md")
        r = self.push()
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("pre-push", r.stderr)

    def publish_schema(self, text):
        """Put memory/schema.json on the remote as an earlier, already-published commit (hook skipped for this setup push)."""
        p = self.repo / "memory/schema.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        git(["add", "memory/schema.json"], self.repo)
        self.assertEqual(git(["commit", "-m", "schema"], self.repo).returncode, 0)
        self.assertEqual(git(["push", "--no-verify", "-u", str(self.bare), "main"], self.repo).returncode, 0)

    def test_push_touching_the_configured_client_folder_is_refused(self):
        self.publish_schema('{"client_folder": "students"}\n')
        self.commit_file("students/ana/notes.md")
        r = self.push()
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("students/ana/notes.md", r.stderr)

    def test_escaped_client_folder_key_cannot_hide_the_folder(self):
        self.publish_schema('{"client\\u005ffolder": "students"}\n')
        self.commit_file("students/ana/notes.md")
        r = self.push()
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("client_folder", r.stderr)

    def test_duplicate_client_folder_key_is_refused(self):
        self.publish_schema('{"client_folder": "clients",\n "client_folder": "students"}\n')
        self.commit_file("students/ana/notes.md")
        r = self.push()
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("client_folder", r.stderr)

    def test_other_checked_out_branch_cannot_hide_the_client_folder(self):
        self.publish_schema('{"client_folder": "students"}\n')
        self.commit_file("students/ana/notes.md")
        git(["checkout", "-b", "other", "HEAD~1"], self.repo)
        (self.repo / "memory/schema.json").write_text('{"client_folder": "clients"}\n')
        git(["commit", "-am", "other schema"], self.repo)
        r = git(["push", str(self.bare), "main"], self.repo)
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("students/ana/notes.md", r.stderr)

    def test_schema_changed_in_the_outgoing_range_protects_the_old_folder_too(self):
        self.publish_schema('{"client_folder": "students"}\n')
        self.commit_file("students/ana/notes.md")
        (self.repo / "memory/schema.json").write_text('{"client_folder": "pupils"}\n')
        git(["add", "memory/schema.json"], self.repo)
        git(["commit", "-m", "rename folder"], self.repo)
        r = self.push()
        self.assertNotEqual(r.returncode, 0, r.stderr)

    def test_unreadable_client_folder_refuses_instead_of_allowing(self):
        self.publish_schema('{"client_folder": "Bad Name"}\n')
        self.commit_file("notes/a.md")
        r = self.push()
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("client_folder", r.stderr)

    def test_private_file_after_a_clean_file_in_the_same_push_is_refused(self):
        self.commit_file("a.txt")
        self.commit_file("memory/caf\u00e9.md")
        self.commit_file("z.txt")
        r = self.push()
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("pre-push", r.stderr)

    def test_one_commit_with_clean_and_private_files_is_refused(self):
        for rel in ("a.txt", "memory/caf\u00e9.md", "src/b.txt"):
            p = self.repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("content\n")
            git(["add", rel], self.repo)
        self.assertEqual(git(["commit", "-m", "mixed"], self.repo).returncode, 0)
        r = self.push()
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("pre-push", r.stderr)

    def test_file_added_only_by_a_merge_commit_is_refused(self):
        self.commit_file("src/base.txt")
        self.assertEqual(self.push().returncode, 0)
        git(["checkout", "-b", "side"], self.repo)
        self.commit_file("src/side.txt")
        git(["checkout", "main"], self.repo)
        self.commit_file("src/main.txt")
        r = git(["merge", "--no-ff", "--no-commit", "side"], self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        p = self.repo / "memory" / "private.md"
        p.parent.mkdir(parents=True)
        p.write_text("private\n")
        git(["add", "memory/private.md"], self.repo)
        r = git(["commit", "-m", "merge side"], self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        parents = git(["rev-list", "--parents", "-n", "1", "HEAD"], self.repo).stdout.split()
        self.assertEqual(len(parents), 3, "HEAD must be a merge commit")
        non_merge = git(["log", "--no-merges", "--name-only", "--format="], self.repo).stdout
        self.assertNotIn("memory/private.md", non_merge, "only the merge commit may introduce it")
        r = self.push()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("memory/private.md", r.stderr)

    def test_unreadable_range_refuses_instead_of_allowing(self):
        self.commit_file("src/a.txt")
        head = git(["rev-parse", "HEAD"], self.repo).stdout.strip()
        bogus = "1" * 40
        r = subprocess.run(["sh", str(HOOK), "origin", str(self.bare)], cwd=self.repo, capture_output=True,
                           text=True, input=f"refs/heads/main {head} refs/heads/main {bogus}\n")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("could not list commits", r.stderr)

    def test_pushing_a_tree_carrying_memory_is_refused(self):
        self.commit_file("memory/p.md")
        tree = git(["rev-parse", "HEAD^{tree}"], self.repo).stdout.strip()
        r = git(["push", str(self.bare), f"{tree}:refs/tags/t"], self.repo)
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("only commits and tags of commits", r.stderr)
        self.assertEqual(git(["tag"], self.bare).stdout.strip(), "", "nothing reached the remote")

    def test_pushing_a_blob_is_refused(self):
        self.commit_file("src/a.txt")
        blob = git(["rev-parse", "HEAD:src/a.txt"], self.repo).stdout.strip()
        r = git(["push", str(self.bare), f"{blob}:refs/tags/b"], self.repo)
        self.assertNotEqual(r.returncode, 0, r.stderr)

    def test_tags_of_clean_and_private_commits(self):
        self.commit_file("src/a.txt")
        git(["tag", "-a", "-m", "clean", "v1"], self.repo)
        self.assertEqual(git(["push", str(self.bare), "v1"], self.repo).returncode, 0)
        self.commit_file("memory/p.md")
        git(["tag", "-a", "-m", "private", "v2"], self.repo)
        r = git(["push", str(self.bare), "v2"], self.repo)
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("memory/p.md", r.stderr)
        git(["tag", "light"], self.repo)
        self.assertNotEqual(git(["push", str(self.bare), "light"], self.repo).returncode, 0)

    def test_no_python_hooks_folder_still_refuses_private_memory(self):
        """INSTALL.md without Python: core.hooksPath .githooks/nopython must keep the push protection."""
        hooks = self.repo / ".githooks"
        (hooks / "nopython").mkdir(parents=True)
        shutil.copy2(HOOK, hooks / "pre-push")
        shutil.copy2(HOOK.parent / "nopython" / "pre-push", hooks / "nopython" / "pre-push")
        git(["config", "core.hooksPath", ".githooks/nopython"], self.repo)
        self.commit_file("memory/mine.md")
        r = self.push()
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("memory/mine.md", r.stderr)

    def test_published_release_repo_may_push_memory(self):
        self.commit_file("memory/starter.md")
        git(["config", "--local", "hooks.publishRelease", "true"], self.repo)
        r = self.push()
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_copy_of_a_published_release_is_protected_again(self):
        git(["config", "--local", "hooks.publishRelease", "true"], self.repo)
        copy = Path(self.tmp.name) / "copy"
        shutil.copytree(self.repo, copy, ignore=shutil.ignore_patterns(".git"))
        git(["init", "-b", "main"], copy)
        git(["config", "core.hooksPath", git(["config", "core.hooksPath"], self.repo).stdout.strip()], copy)
        git(["config", "user.name", "Owner"], copy)
        git(["config", "user.email", "owner@example.com"], copy)
        p = copy / "memory" / "mine.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("private\n")
        git(["add", "-A"], copy)
        self.assertEqual(git(["commit", "-m", "mine"], copy).returncode, 0)
        r = git(["push", str(self.bare), "main:refs/heads/copy"], copy)
        self.assertNotEqual(r.returncode, 0, r.stderr)
        self.assertIn("memory/mine.md", r.stderr)

    def test_publish_setting_must_be_exactly_true(self):
        self.commit_file("memory/p.md")
        git(["config", "--local", "hooks.publishRelease", "yes"], self.repo)
        self.assertNotEqual(self.push().returncode, 0)


if __name__ == "__main__":
    unittest.main()