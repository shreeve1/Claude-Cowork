import contextlib
import errno
import io
import json
import os
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import meetings as m

OLD = time.time() - 3600
LAST_CHECK = 3  # file_hashes calls in copy_then_remove: copy, source, source again before removing it
DOCX_XML = ("<w:document><w:body><w:p><w:r><w:t>Ana</w:t><w:tab/><w:t>said hi &amp; left</w:t></w:r></w:p>"
            "<w:p><w:r><w:t>Line two</w:t></w:r></w:p></w:body></w:document>")


def age(path: Path, when: float = OLD) -> None:
    for p in [path, *path.rglob("*")] if path.is_dir() else [path]:
        os.utime(p, (when, when))


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class MeetingsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "work space"
        self.folder = self.root / "Transcripts"
        write(self.folder / "2026-10-20 Supplier call.txt", "Ana: we ship Friday.\nMe: I will send the PO.")
        write(self.folder / "Standup.vtt", "WEBVTT\n\nNOTE exported by app\nsecond note line\n\n"
                                           "1\n00:00:01.000 --> 00:00:04.000\n<v Ana>Hello team</v>\n\n"
                                           "2\n00:01:02.500 --> 00:01:05.000\nSecond line\n")
        write(self.folder / "café review.srt", "1\n00:00:01,000 --> 00:00:02,000\nBonjour\n")
        folder_meeting = self.folder / "Meeting 21_10_26"
        write(folder_meeting / "transcripts.json", json.dumps(
            {"text": "one two", "segments": [{"text": "one", "speaker": "Ana"}, {"text": "two"}]}))
        write(folder_meeting / "metadata.json", json.dumps({"duration": 3}))
        write(folder_meeting / "audio.mp4", "x")
        with zipfile.ZipFile(self.folder / "Teams export.docx", "w") as z:
            z.writestr("word/document.xml", DOCX_XML)
        write(self.folder / "empty.txt", "   ")
        write(self.folder / "photo.png", "x")
        write(self.folder / ".hidden.txt", "x")
        write(self.folder / "Archive" / "old.txt", "done")
        age(self.folder)

    def tearDown(self):
        self.tmp.cleanup()

    def scan(self, now=None):
        return m.scan(self.folder, self.folder / "Archive", self.root, now)

    def item(self, key):
        return m.find(self.scan(), key, self.folder)

    def test_lists_transcripts_and_skips_the_rest(self):
        keys = {i["key"]: i for i in self.scan()}
        self.assertEqual(set(keys), {"2026-10-20-supplier-call", "standup", "café-review", "meeting-21-10-26",
                                     "teams-export", "empty"})
        self.assertEqual(keys["meeting-21-10-26"]["kind"], "folder")
        self.assertEqual(keys["empty"]["words"], 0)
        self.assertEqual(keys["standup"]["path"], "Transcripts/Standup.vtt")
        self.assertFalse(any(i["settling"] for i in keys.values()))

    def test_cue_files_lose_numbers_and_timings(self):
        self.assertEqual(m.transcript(self.folder / "Standup.vtt"), "00:00:01 Ana: Hello team\n00:01:02 Second line")
        self.assertEqual(m.transcript(self.folder / "café review.srt"), "00:00:01 Bonjour")

    def test_json_reads_segments_once_and_skips_files_without_text(self):
        text = m.transcript(self.folder / "Meeting 21_10_26")
        self.assertEqual(text, "## transcripts.json\n\nAna: one\ntwo")

    def test_docx_paragraphs(self):
        self.assertEqual(m.transcript(self.folder / "Teams export.docx"), "Ana said hi & left\nLine two")

    def test_records_are_matched_by_transcript_hash_then_by_name(self):
        item = self.item("standup")
        write(self.root / "clients" / "acme" / "meetings" / "2026-10-20-standup.md",
              f"---\ntype: meeting-record\nsource: Standup.vtt\ntranscript_hash: {item['transcript_hash']}  # set\n---\n")
        write(self.root / "notes" / "meetings" / "2026-10-21-supplier.md",
              "---\ntype: meeting-record\nsource: \"2026-10-20 Supplier call.txt\"\ntranscript_hash: 000000000000\n---\n")
        write(self.root / "notes" / "meetings" / "not-a-record.md", "---\ntype: note\nsource: café review.srt\n---\n")
        items = {i["key"]: i for i in self.scan()}
        self.assertEqual(items["standup"]["record"], "clients/acme/meetings/2026-10-20-standup.md")
        self.assertIsNone(items["standup"]["same_name_record"])
        self.assertIsNone(items["2026-10-20-supplier-call"]["record"])
        self.assertEqual(items["2026-10-20-supplier-call"]["same_name_record"], "notes/meetings/2026-10-21-supplier.md")
        self.assertIsNone(items["café-review"]["same_name_record"])

    def test_same_text_under_another_name_is_not_done(self):
        item = self.item("standup")
        write(self.root / "notes" / "meetings" / "2026-10-20-standup.md",
              f"---\ntype: meeting-record\nsource: Standup.vtt\ntranscript_hash: {item['transcript_hash']}\n---\n")
        write(self.folder / "Standup copy.vtt", (self.folder / "Standup.vtt").read_text(encoding="utf-8"))
        age(self.folder / "Standup copy.vtt")
        copy = self.item("standup-copy")
        self.assertIsNone(copy["record"])
        self.assertEqual(copy["same_text_record"], "notes/meetings/2026-10-20-standup.md")
        self.assertEqual(self.item("standup")["record"], "notes/meetings/2026-10-20-standup.md")

    def test_find_by_a_path_inside_the_meeting(self):
        hit = m.find(self.scan(), str(self.folder / "Meeting 21_10_26" / "transcripts.json"), self.folder)
        self.assertEqual(hit["key"], "meeting-21-10-26")
        with self.assertRaises(SystemExit):
            m.find(self.scan(), str(self.root / "elsewhere.txt"), self.folder)

    def test_archive_moves_and_never_overwrites(self):
        dest = m.archive(self.item("standup"), self.folder, self.folder / "Archive")
        self.assertEqual(dest, self.folder / "Archive" / "Standup.vtt")
        self.assertFalse((self.folder / "Standup.vtt").exists())
        write(self.folder / "Standup.vtt", "WEBVTT\n\nnext week\n")
        age(self.folder / "Standup.vtt")
        second = m.archive(self.item("standup"), self.folder, self.folder / "Archive")
        self.assertEqual(second.name, "Standup (2).vtt")
        self.assertIn("Hello team", dest.read_text(encoding="utf-8"))
        self.assertNotIn("standup", [i["key"] for i in self.scan()])

    def test_archive_never_replaces_a_name_taken_after_the_check(self):
        real = m.free_name
        taken = self.folder / "Archive" / "Standup.vtt"

        def race(folder, name, is_file):
            dest = real(folder, name, is_file)
            if dest == taken and not taken.exists():
                write(taken, "someone else's file")
            return dest

        with mock.patch.object(m, "free_name", side_effect=race):
            dest = m.archive(self.item("standup"), self.folder, self.folder / "Archive")
        self.assertEqual(taken.read_text(encoding="utf-8"), "someone else's file")
        self.assertEqual(dest.name, "Standup (2).vtt")
        self.assertFalse((self.folder / "Standup.vtt").exists())

    def test_archive_moves_a_folder_meeting_whole(self):
        dest = m.archive(self.item("meeting-21-10-26"), self.folder, self.folder / "Archive")
        self.assertTrue((dest / "audio.mp4").exists())
        self.assertFalse((self.folder / "Meeting 21_10_26").exists())

    def test_archive_refuses_a_meeting_still_being_written(self):
        os.utime(self.folder / "Meeting 21_10_26" / "metadata.json")
        item = self.item("meeting-21-10-26")
        self.assertTrue(item["settling"])
        with self.assertRaises(SystemExit):
            m.archive(item, self.folder, self.folder / "Archive")
        self.assertTrue((self.folder / "Meeting 21_10_26").exists())

    def test_archive_across_drives_copies_checks_then_removes(self):
        real = os.rename
        src = self.folder / "Meeting 21_10_26"

        def cross_drive(a, b):
            if Path(a) == src:
                raise OSError(errno.EXDEV, "cross-device link")
            return real(a, b)

        with mock.patch.object(m.os, "rename", side_effect=cross_drive), \
                mock.patch.object(m.os, "link", side_effect=OSError(errno.EXDEV, "cross-device link")):
            dest = m.archive(self.item("meeting-21-10-26"), self.folder, self.root / "Elsewhere")
        self.assertFalse(src.exists())
        self.assertEqual((dest / "metadata.json").read_text(encoding="utf-8"), json.dumps({"duration": 3}))
        self.assertFalse(dest.with_name(dest.name + ".partial").exists())

    def test_a_source_written_during_the_copy_is_kept(self):
        src = self.folder / "2026-10-20 Supplier call.txt"
        real = m.file_hashes
        calls = []

        def late_write(p):
            calls.append(p)
            if len(calls) == LAST_CHECK:
                write(src, "a late line")
            return real(p)

        real_rename, real_link = os.rename, os.link

        def cross_drive(fn):
            def call(a, b):
                if Path(a) == src:
                    raise OSError(errno.EXDEV, "cross-device link")
                return fn(a, b)
            return call

        with mock.patch.object(m.os, "rename", side_effect=cross_drive(real_rename)), \
                mock.patch.object(m.os, "link", side_effect=cross_drive(real_link)), \
                mock.patch.object(m, "file_hashes", side_effect=late_write), self.assertRaises(SystemExit):
            m.archive(self.item("2026-10-20-supplier-call"), self.folder, self.root / "Elsewhere")
        self.assertEqual(src.read_text(encoding="utf-8"), "a late line")
        self.assertTrue((self.root / "Elsewhere" / src.name).exists())

    def test_a_failed_copy_leaves_no_partial(self):
        exdev = OSError(errno.EXDEV, "cross-device link")
        with mock.patch.object(m.os, "rename", side_effect=exdev), mock.patch.object(m.os, "link", side_effect=exdev), \
                mock.patch.object(m.shutil, "copy2", side_effect=lambda a, b: (write(Path(b), "half"),
                                                                              (_ for _ in ()).throw(OSError("disk full")))), \
                self.assertRaises(SystemExit):
            m.archive(self.item("2026-10-20-supplier-call"), self.folder, self.root / "Elsewhere")
        self.assertTrue((self.folder / "2026-10-20 Supplier call.txt").exists())
        self.assertEqual(list((self.root / "Elsewhere").iterdir()), [])

    def test_a_bad_copy_leaves_the_source_alone(self):
        src = self.folder / "2026-10-20 Supplier call.txt"
        hashes = iter([{"a": "1"}, {"a": "2"}])
        exdev = OSError(errno.EXDEV, "cross-device link")
        with mock.patch.object(m.os, "rename", side_effect=exdev), mock.patch.object(m.os, "link", side_effect=exdev), \
                mock.patch.object(m, "file_hashes", side_effect=lambda p: next(hashes)), \
                self.assertRaises(SystemExit):
            m.archive(self.item("2026-10-20-supplier-call"), self.folder, self.root / "Elsewhere")
        self.assertTrue(src.exists())
        self.assertEqual(list((self.root / "Elsewhere").iterdir()), [])

    def test_cli_list_and_missing_folder(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(m.main(["--folder", str(self.folder), "--root", str(self.root), "list"]), 0)
        self.assertEqual(len(json.loads(out.getvalue())), 6)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(m.main(["--folder", str(self.root / "nope"), "list"]), 1)


if __name__ == "__main__":
    unittest.main()
