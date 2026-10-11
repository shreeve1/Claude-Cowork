"""The edition pre-commit hook blocks credential-looking lines, except exact lines a maintainer reviewed.

A reviewed line is identified by the sha256 of its stripped text and a path prefix, so a new or changed
credential in the same folder still blocks the commit.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "pre-commit"
LIB = "lib/"
REVIEWED = "pass" + "word: " + "hunter2" * 2
NEW = "api" + "_key: " + "abcdefgh" + "12345678"


def git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


class PreCommitAllowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(["init", "-q", "-b", "main"], self.repo)
        git(["config", "user.name", "Test"], self.repo)
        git(["config", "user.email", "t@example.com"], self.repo)
        hooks = self.repo / ".githooks"
        hooks.mkdir()
        shutil.copy2(HOOK, hooks / "pre-commit")
        git(["config", "core.hooksPath", ".githooks"], self.repo)
        self.addCleanup(self.tmp.cleanup)

    def allow(self, lines, prefix=LIB):
        digests = [hashlib.sha256(x.strip().encode("utf-8")).hexdigest() for x in lines]
        (self.repo / ".githooks" / "secret-allow.json").write_text(
            json.dumps({"reviewed": [{"prefix": prefix, "line_sha256": digests, "reason": "t"}]}), encoding="utf-8")

    def commit(self, rel, text):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        git(["add", rel], self.repo)
        return git(["commit", "-m", "x"], self.repo)

    def test_unreviewed_credential_line_blocks_the_commit(self):
        r = self.commit(LIB + "a.md", REVIEWED + "\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("possible secret", r.stderr)

    def test_reviewed_line_passes_at_its_path_only(self):
        self.allow([REVIEWED])
        self.assertEqual(self.commit(LIB + "a.md", REVIEWED + "\n").returncode, 0)
        r = self.commit("other/b.md", REVIEWED + "\n")
        self.assertNotEqual(r.returncode, 0, "the same line outside the reviewed path must still block")

    def test_new_credential_in_the_reviewed_folder_still_blocks(self):
        self.allow([REVIEWED])
        r = self.commit(LIB + "c.md", REVIEWED + "\n" + NEW + "\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("api_key", r.stderr)

    def test_a_changed_reviewed_line_blocks(self):
        self.allow([REVIEWED])
        r = self.commit(LIB + "d.md", REVIEWED + "x\n")
        self.assertNotEqual(r.returncode, 0)

    def test_a_reviewed_private_key_header_still_blocks(self):
        header = "-----BEGIN RSA " + "PRIVATE KEY-----"
        self.allow([header])
        r = self.commit(LIB + "k.md", header + "\nQUJD\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("private key", r.stderr)


if __name__ == "__main__":
    unittest.main()
