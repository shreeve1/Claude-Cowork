import base64
import sys
import tempfile
import unittest
import urllib.parse
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import link  # noqa: E402

XML = '<mxfile><diagram id="p" name="Page-1"><mxGraphModel><root><mxCell id="0"/>' \
      '<mxCell id="a" value="Ünïcode &amp; spaces" vertex="1" parent="0"/></root></mxGraphModel></diagram></mxfile>\n'


def decode(url):
    data = urllib.parse.unquote(url.split("#R", 1)[1])
    return urllib.parse.unquote(zlib.decompress(base64.b64decode(data), -15).decode("ascii"))


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.td = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.td, ignore_errors=True))

    def test_link_round_trips_the_file_and_names_it(self):
        p = self.td / "email triage.drawio"
        p.write_text(XML, encoding="utf-8")
        url = link.link(p)
        self.assertTrue(url.startswith("https://app.diagrams.net/?title=email%20triage.drawio#R"))
        self.assertEqual(decode(url), XML)
        self.assertNotIn("+", url.split("#R", 1)[1])

    def test_bom_and_crlf_do_not_reach_the_link(self):
        p = self.td / "a.drawio"
        p.write_bytes(b"\xef\xbb\xbf" + XML.replace("\n", "\r\n").encode("utf-8"))
        self.assertEqual(decode(link.link(p)), XML)

    def test_unreadable_or_too_long_is_reported(self):
        p = self.td / "b.drawio"
        p.write_bytes(b"\xff\xfe<mxfile/>")
        self.assertEqual(link.main([str(p)]), 2)
        p.write_text("<mxfile/>", encoding="utf-8")
        self.addCleanup(setattr, link, "MAX_LINK", link.MAX_LINK)
        link.MAX_LINK = 10
        self.assertEqual(link.main([str(p)]), 1)

    def test_missing_file_is_a_usage_error(self):
        self.assertEqual(link.main([str(self.td / "nope.drawio")]), 2)


if __name__ == "__main__":
    unittest.main()
