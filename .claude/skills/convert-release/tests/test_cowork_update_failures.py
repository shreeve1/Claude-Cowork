import subprocess
import sys
import unittest
from unittest import mock

import test_cowork_update as base


class FailureTests(base.UpdateTests):
    def child(self, tx, command, point):
        code = """import importlib.util,os,sys
from pathlib import Path
s=importlib.util.spec_from_file_location('engine',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def stop(name):
 if name==sys.argv[5]: os._exit(137)
f=getattr(m,sys.argv[3]);f(Path(sys.argv[2]),sys.argv[4],checkpoint=stop)
"""
        return subprocess.run(
            [
                sys.executable,
                "-I",
                "-c",
                code,
                str(base.ENGINE),
                str(tx),
                command,
                self.identifier(tx),
                point,
            ],
            capture_output=True,
            text=True,
        )

    def test_update_interruption_boundaries_restore_in_fresh_process(self):
        self.load()
        for point in (
            "apply_intent:config.md",
            "apply_temp:config.md",
            "apply_write:config.md",
            "apply_write:new/deep/file.md",
            "apply_remove:old/remove.md",
            "apply_complete",
        ):
            with self.subTest(point=point):
                self.setUp()
                before = self.snapshot()
                tx = self.prepare()
                result = self.child(tx, "apply_transaction", point)
                self.assertEqual(result.returncode, 137, result.stdout + result.stderr)
                self.load().rollback_transaction(tx, self.identifier(tx))
                self.assertEqual(self.snapshot(), before)

    def test_restore_interruption_boundaries_are_restartable(self):
        self.load()
        for point in (
            "restore_intent:config.md",
            "restore_move:config.md",
            "restore_temp:config.md",
            "restore_write:config.md",
            "restore_move:new/deep/file.md",
            "restore_dir:new",
            "restore_complete",
        ):
            with self.subTest(point=point):
                self.setUp()
                before = self.snapshot()
                tx = self.prepare()
                self.load().apply_transaction(tx, self.identifier(tx))
                result = self.child(tx, "rollback_transaction", point)
                self.assertEqual(result.returncode, 137, result.stdout + result.stderr)
                self.load().rollback_transaction(tx, self.identifier(tx))
                self.assertEqual(self.snapshot(), before)

    def test_failure_stops_later_operations_and_recovers(self):
        tx = self.prepare()
        e = self.load()
        original = e.os.replace

        def fail(src, dst):
            if str(dst).endswith("config.md"):
                raise OSError("injected replacement failure")
            return original(src, dst)

        with mock.patch.object(e.os, "replace", side_effect=fail), self.assertRaises(OSError):
            e.apply_transaction(tx, self.identifier(tx))
        self.assertFalse((self.ws / "new").exists())
        self.assertEqual((self.ws / "old/remove.md").read_bytes(), b"retired\n")
        e.rollback_transaction(tx, self.identifier(tx))
        self.assertEqual((self.ws / "config.md").read_bytes(), b"owner\r\n")

    def test_tampered_interrupted_restore_temp_is_not_overwritten(self):
        tx = self.prepare()
        e = self.load()
        e.apply_transaction(tx, self.identifier(tx))
        result = self.child(tx, "rollback_transaction", "restore_temp:config.md")
        self.assertEqual(result.returncode, 137)
        temporary = next(p for p in self.ws.iterdir() if ".cowork-" in p.name)
        temporary.write_bytes(b"owner wrote here")
        before = self.snapshot()
        with self.assertRaises(e.UpdateError):
            e.rollback_transaction(tx, self.identifier(tx))
        self.assertEqual(self.snapshot(), before)

    def test_matching_unjournaled_new_file_is_not_update_owned(self):
        tx = self.prepare()
        e = self.load()
        self.put("new/deep/file.md", b"added\n")
        before = self.snapshot()
        with self.assertRaises(e.UpdateError):
            e.rollback_transaction(tx, self.identifier(tx))
        self.assertEqual(self.snapshot(), before)

    def test_restore_write_failure_does_not_displace_current_file(self):
        tx = self.prepare()
        e = self.load()
        e.apply_transaction(tx, self.identifier(tx))
        before = self.snapshot()
        original = e.write_new

        def partial(path, data):
            if str(path).endswith("-restore.tmp"):
                path.write_bytes(data[:2])
                raise OSError("injected partial write")
            return original(path, data)

        with mock.patch.object(e, "write_new", side_effect=partial), self.assertRaises(OSError):
            e.rollback_transaction(tx, self.identifier(tx))
        self.assertEqual((self.ws / "config.md").read_bytes(), before["config.md"])
        e.rollback_transaction(tx, self.identifier(tx))
        self.assertEqual((self.ws / "config.md").read_bytes(), b"owner\r\n")

    def test_interrupted_preparation_is_retained_but_does_not_block(self):
        e = self.load()

        def stop(point):
            if point == "prepare_created":
                raise OSError("preparation interrupted")

        with self.assertRaises(OSError):
            e.prepare_transaction(self.ws, self.spec, checkpoint=stop)
        self.assertTrue(list((self.ws / e.STORAGE).glob(".preparing-*")))
        tx = self.prepare()
        self.assertEqual(e.transaction_status(tx)["state"], "prepared")

    def test_lock_excludes_other_helper_process(self):
        tx = self.prepare()
        e = self.load()
        with e.workspace_lock(self.ws):
            result = self.child(tx, "apply_transaction", "never")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.ws / "config.md").read_bytes(), b"owner\r\n")


if __name__ == "__main__":
    unittest.main()
