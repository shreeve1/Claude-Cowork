import contextlib
import http.server
import io
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import watch  # noqa: E402

OLD = time.time() - watch.SETTLE - 60


class Page(http.server.BaseHTTPRequestHandler):
    body = b""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(Page.body)

    def log_message(self, *a):
        pass


class WatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.dir = self.tmp / "meetings"
        self.dir.mkdir()
        self.cfg = self.tmp / "startday.json"
        self.state = self.tmp / "state.json"

    def config(self, *targets):
        self.cfg.write_text(json.dumps({"watch": list(targets)}))

    def run_watch(self, ack=True):
        """One poll turn: report, then (by default) ack as a turn that handled everything would."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = watch.main(["--config", str(self.cfg), "--state", str(self.state)])
        result = (code, json.loads(out.getvalue()) if code == 0 else None)
        if ack and code == 0:
            with contextlib.redirect_stdout(io.StringIO()):
                watch.main(["--state", str(self.state), "--ack"])
        return result

    def file(self, name, text, mtime=OLD):
        p = self.dir / name
        p.write_text(text)
        os.utime(p, (mtime, mtime))
        return p

    def test_look_back_key_beside_watch_is_ignored(self):
        self.cfg.write_text(json.dumps({"watch": [{"path": str(self.dir)}], "look_back": True}))
        self.assertEqual(self.run_watch(), (0, []))
        self.file("a.md", "one")
        code, out = self.run_watch()
        self.assertEqual((code, [c["change"] for c in out]), (0, ["new"]))

    def test_manual_state_key_survives_a_script_run(self):
        """The by-hand method keeps its state under "manual" in the same file; the script must not drop it."""
        self.config({"path": str(self.dir)})
        self.state.write_text(json.dumps({"manual": {"files": {"x": {"a": "1:2"}}, "pending": {}}}))
        self.run_watch()
        self.assertEqual(json.loads(self.state.read_text())["manual"], {"files": {"x": {"a": "1:2"}}, "pending": {}})

    def test_folder_baseline_then_new_changed_gone(self):
        self.config({"path": str(self.dir), "use": "meetings"})
        a = self.file("a.md", "one")
        self.assertEqual(self.run_watch(), (0, []))
        self.file("b.md", "two")
        self.file("a.md", "one edited")
        code, out = self.run_watch()
        self.assertEqual(sorted((c["change"], Path(c["file"]).name) for c in out),
                         [("changed", "a.md"), ("new", "b.md")])
        self.assertEqual(out[0]["use"], "meetings")
        self.assertEqual({c["id"] for c in out}, {watch.path_id(self.dir / "a.md"), watch.path_id(self.dir / "b.md")})
        a.unlink()
        code, out = self.run_watch()
        self.assertEqual([(c["change"], Path(c["file"]).name) for c in out], [("gone", "a.md")])
        self.assertEqual(self.run_watch(), (0, []))

    def test_file_still_being_written_waits_for_settle(self):
        self.config({"path": str(self.dir)})
        self.run_watch()
        p = self.file("live.md", "half", mtime=time.time())
        self.assertEqual(self.run_watch(), (0, []))
        os.utime(p, (OLD, OLD))
        code, out = self.run_watch()
        self.assertEqual([(c["change"], Path(c["file"]).name) for c in out], [("new", "live.md")])

    def test_known_file_rewritten_inside_settle_is_not_reported_gone(self):
        self.config({"path": str(self.dir)})
        p = self.file("a.md", "one")
        self.run_watch()
        self.file("a.md", "longer", mtime=time.time())
        self.assertEqual(self.run_watch(), (0, []))
        os.utime(p, (OLD, OLD))
        code, out = self.run_watch()
        self.assertEqual([c["change"] for c in out], ["changed"])

    def test_unacked_change_is_reported_again_and_new_stays_new(self):
        """A turn that dies before handling a transcript must not lose it."""
        self.config({"path": str(self.dir), "use": "meetings"})
        self.run_watch()
        self.file("t.md", "first part")
        code, out = self.run_watch(ack=False)
        self.assertEqual([(c["change"], c["id"]) for c in out], [("new", watch.path_id(self.dir / "t.md"))])
        self.file("t.md", "first part, fixed")
        code, again = self.run_watch(ack=False)
        self.assertEqual([c["change"] for c in again], ["new"])
        self.assertEqual(again[0]["id"], out[0]["id"])
        self.assertNotEqual(again[0]["sha256"], out[0]["sha256"])
        self.run_watch()
        self.assertEqual(self.run_watch(), (0, []))

    def test_unreadable_target_does_not_block_the_others(self):
        bad = self.tmp / "bad"
        bad.mkdir()
        self.config({"path": str(bad)}, {"path": str(self.dir)})
        self.run_watch()
        self.file("a.md", "x")
        real = watch.files_under
        watch.files_under = lambda root: (_ for _ in ()).throw(PermissionError("denied")) if root == bad else real(root)
        self.addCleanup(setattr, watch, "files_under", real)
        code, out = self.run_watch()
        self.assertEqual(sorted(c["change"] for c in out), ["error", "new"])

    def test_missing_target_reports_error_and_bad_config_exits_1(self):
        self.config({"path": str(self.tmp / "nope")})
        code, out = self.run_watch()
        self.assertEqual([c["change"] for c in out], ["error"])
        self.config({"path": "x", "url": "y"})
        self.assertEqual(self.run_watch(), (1, None))
        self.cfg.write_text("{}")
        self.assertEqual(self.run_watch(), (1, None))

    def test_page_compares_visible_text_and_failure_keeps_baseline(self):
        srv = http.server.HTTPServer(("127.0.0.1", 0), Page)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.shutdown)
        url = f"http://127.0.0.1:{srv.server_port}/"
        self.config({"url": url, "why": "outages"})
        Page.body = b"<html><script>var t=1</script><p>All systems up</p></html>"
        self.assertEqual(self.run_watch(), (0, []))
        Page.body = b"<html><script>var t=2</script><div><p>All systems up</p></div></html>"
        self.assertEqual(self.run_watch(), (0, []))
        Page.body = b"<html><p>Email degraded</p></html>"
        code, out = self.run_watch()
        self.assertEqual(out[0]["change"], "changed")
        self.assertIn("+Email degraded", out[0]["diff"])
        self.assertIn("-All systems up", out[0]["diff"])
        Page.body = b"<html><p>-- signature</p></html>"
        code, out = self.run_watch()
        self.assertIn("+-- signature", out[0]["diff"])
        self.assertIn("-Email degraded", out[0]["diff"])
        srv.shutdown()
        srv.server_close()
        code, out = self.run_watch()
        self.assertEqual([c["change"] for c in out], ["error"])
        self.assertEqual(json.loads(self.state.read_text())["pages"][url], "-- signature")


if __name__ == "__main__":
    unittest.main()
