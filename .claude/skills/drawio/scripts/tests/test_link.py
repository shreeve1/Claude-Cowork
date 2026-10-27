import base64
import html
import re
import sys
import tempfile
import unittest
import urllib.parse
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import link  # noqa: E402

XML = '<mxfile><diagram id="p" name="Page-1"><mxGraphModel><root><mxCell id="0"/>' \
      '<mxCell id="a" value="Ünïcode &amp; spaces" vertex="1" parent="0"><mxGeometry width="160" height="60" as="geometry"/>' \
      '</mxCell></root></mxGraphModel></diagram></mxfile>\n'


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

    def test_html_preview_draws_the_diagram_offline_with_the_edit_link(self):
        p, out = self.td / "a.drawio", self.td / "previews" / "a.html"
        p.write_text(XML, encoding="utf-8")
        self.assertEqual(link.main([str(p), "--html", str(out)]), 0)
        page = out.read_text(encoding="utf-8")
        self.assertEqual(html.unescape(re.search(r'<a href="([^"]+)"', page).group(1)), link.link(p))
        self.assertIn("<svg", page)
        self.assertIn("Ünïcode &amp; spaces", page)
        self.assertEqual(re.findall(r'(?:src|href)="(https?:[^"]+)"', page), [link.link(p).replace("&", "&amp;")])

    def test_unparseable_diagram_still_gets_its_link(self):
        p, out = self.td / "bad.drawio", self.td / "bad.html"
        p.write_text("<mxfile><diagram>", encoding="utf-8")
        self.assertEqual(link.main([str(p), "--html", str(out)]), 1)
        self.assertFalse(out.exists())

    def test_preview_escapes_the_file_name(self):
        p, out = self.td / "a&b'c.drawio", self.td / "a.html"  # < and > aren't allowed in Windows names
        p.write_text(XML, encoding="utf-8")
        self.assertEqual(link.main([str(p), "--html", str(out)]), 0)
        page = out.read_text(encoding="utf-8")
        self.assertIn("<title>a&amp;b&#x27;c.drawio</title>", page)
        self.assertNotIn("a&b'c", page)

    def test_compressed_page_that_is_not_utf8_still_previews(self):
        bad = base64.b64encode(zlib.compress(b"\xff\xfe", 9)[2:-4]).decode()
        p, out = self.td / "c.drawio", self.td / "c.html"
        p.write_text(f'<mxfile><diagram name="x">{bad}</diagram></mxfile>', encoding="utf-8")
        self.assertIn(link.main([str(p), "--html", str(out)]), (0, 1))

    def test_preview_never_overwrites_the_diagram_or_follows_a_too_long_link(self):
        p = self.td / "keep.drawio"
        p.write_text(XML, encoding="utf-8")
        self.assertEqual(link.main([str(p), "--html", str(p)]), 2)
        self.assertEqual(p.read_text(encoding="utf-8"), XML)
        self.addCleanup(setattr, link, "MAX_LINK", link.MAX_LINK)
        link.MAX_LINK = 10
        self.assertEqual(link.main([str(p), "--html", str(self.td / "long.html")]), 1)
        self.assertFalse((self.td / "long.html").exists())

    def test_missing_file_is_a_usage_error(self):
        self.assertEqual(link.main([str(self.td / "nope.drawio")]), 2)


if __name__ == "__main__":
    unittest.main()
