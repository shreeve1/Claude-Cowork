import base64
import re
import sys
import unittest
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import svg  # noqa: E402

MODEL = """<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="a" value="Start &amp;lt;here&amp;gt;" style="ellipse;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="40" width="160" height="60" as="geometry"/></mxCell>
<mxCell id="lane" value="Lane" style="swimlane;startSize=30;" vertex="1" parent="1">
  <mxGeometry x="400" y="300" width="200" height="140" as="geometry"/></mxCell>
<mxCell id="b" value="Line one&lt;br&gt;line two" style="rounded=1;fillColor=#dae8fc;" vertex="1" parent="lane">
  <mxGeometry x="20" y="50" width="160" height="60" as="geometry"/></mxCell>
<mxCell id="e" value="yes" style="edgeStyle=orthogonalEdgeStyle;dashed=1;" edge="1" parent="1" source="a" target="b">
  <mxGeometry relative="1" as="geometry"/></mxCell>
</root></mxGraphModel>"""


def compressed(xml):
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(c.compress(urllib.parse.quote(xml, safe="").encode()) + c.flush()).decode()


class SvgTests(unittest.TestCase):
    def draw(self, xml):
        found = svg.pages(xml)
        out = svg.svg(found[0][1])
        ET.fromstring(out)  # well-formed
        return found, out

    def test_shapes_labels_and_edges_are_drawn(self):
        _, out = self.draw(f'<mxfile><diagram name="Main">{MODEL}</diagram></mxfile>')
        self.assertIn("<ellipse", out)
        self.assertIn("Start &lt;here&gt;", out)
        self.assertIn(">Line one</tspan>", out)
        self.assertIn(">line two</tspan>", out)
        self.assertIn('fill="#dae8fc"', out)
        self.assertIn('stroke-dasharray="5 4" marker-end="url(#arrow)"', out)

    def test_child_of_a_container_is_placed_inside_it(self):
        _, out = self.draw(MODEL)
        self.assertRegex(out, r'<rect x="420\.0" y="350\.0" width="160\.0" height="60\.0" rx="10')

    def test_compressed_pages_are_decoded_and_counted(self):
        found, out = self.draw(f'<mxfile><diagram name="One">{compressed(MODEL)}</diagram>'
                               '<diagram name="Two"><mxGraphModel><root/></mxGraphModel></diagram></mxfile>')
        self.assertEqual([n for n, _ in found], ["One", "Two"])
        self.assertIn("Lane", out)

    def test_wrapped_cells_keep_their_id_label_and_edges(self):
        _, out = self.draw("""<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>
<UserObject id="u1" label="Wrapped one" owner="x"><mxCell style="rounded=0;" vertex="1" parent="1">
  <mxGeometry x="0" y="0" width="120" height="60" as="geometry"/></mxCell></UserObject>
<object id="u2" label="Wrapped two"><mxCell style="ellipse;" vertex="1" parent="1">
  <mxGeometry x="0" y="200" width="120" height="60" as="geometry"/></mxCell></object>
<mxCell id="e" edge="1" parent="1" source="u1" target="u2"><mxGeometry relative="1" as="geometry"/></mxCell>
</root></mxGraphModel>""")
        self.assertIn("Wrapped one", out)
        self.assertIn("Wrapped two", out)
        self.assertIn("<ellipse", out)
        self.assertIn('marker-end="url(#arrow)"', out)

    def test_bad_values_never_crash_or_escape(self):
        _, out = self.draw("""<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="a" parent="b" vertex="1" value="&quot; onload=&quot;alert(1)"
  style="fillColor=&quot; onload=&quot;x;strokeColor=default;fontColor=url(#y);swimlane;startSize=big">
  <mxGeometry x="ten" y="5" width="100" height="40" as="geometry"/></mxCell>
<mxCell id="b" parent="a" vertex="1" style="fillColor=default"><mxGeometry width="50" height="50" as="geometry"/></mxCell>
</root></mxGraphModel>""")
        root = ET.fromstring(out)
        self.assertFalse([el for el in root.iter() if "onload" in el.attrib])
        self.assertNotIn('"default"', out)
        self.assertNotIn("url(#y)", out)
        self.assertIn('fill="#ffffff" stroke="#1d1d1f"', out)

    def test_empty_page_still_gives_an_svg(self):
        _, out = self.draw('<mxfile><diagram><mxGraphModel><root><mxCell id="0"/></root></mxGraphModel></diagram></mxfile>')
        self.assertTrue(re.match(r'<svg [^>]*viewBox="', out))


if __name__ == "__main__":
    unittest.main()
