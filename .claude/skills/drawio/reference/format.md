# .drawio file format and editing rules

## Anatomy

```xml
<mxfile host="drawio">
  <diagram id="page-1" name="Page-1">
    <mxGraphModel dx="800" dy="600" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- every shape and arrow goes here, parent="1" (or a container's id) -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

- Cells `0` and `1` are required: `0` is the root, `1` the default layer. Never remove or renumber them.
- Each `<diagram>` is a page (tab). Most files have one.
- **Shape (vertex):** `<mxCell id="…" value="label" style="…" vertex="1" parent="1"><mxGeometry x="…" y="…" width="…" height="…" as="geometry"/></mxCell>`
- **Arrow (edge):** `<mxCell id="…" value="optional label" style="…" edge="1" parent="1" source="<shape id>" target="<shape id>"><mxGeometry relative="1" as="geometry"/></mxCell>`. An edge's `<mxGeometry>` may contain `<Array as="points">` waypoints the owner added; keep them.
- **Compressed pages:** if `<diagram>` contains a base64 blob instead of `<mxGraphModel>`, it was saved compressed (`encodeURIComponent`, then deflate-raw, then base64). Decode it to edit: `python3 -c "import base64,sys,urllib.parse,zlib; print(urllib.parse.unquote(zlib.decompress(base64.b64decode(sys.argv[1]),-15).decode()))" '<blob>'`, and write the page back uncompressed. To stop it happening again, ask the owner to untick **File > Properties > Compressed** in draw.io and save.

## Editing without wrecking the owner's work

- **Change only what was asked.** Leave the `id`, `style` and `<mxGeometry>` of existing cells exactly as they are. Layout is the owner's: don't move their shapes to tidy up.
- **Edit in place**, with targeted edits to the cells concerned. Rewrite the whole file only when creating it.
- **New ids:** unique and readable, from the label: `step-validate`, `dec-has-attachment`, `edge-validate-to-route`.
- **Deleting a shape:** also delete every edge whose `source` or `target` is that shape, and any cell whose `parent` is it.
- **Labels:** XML-escape (`&amp;` `&lt;` `&gt;` `&quot;`). With `html=1` in the style, a line break is `&lt;br&gt;`.
- **Placement:** put new shapes in empty space, near what they connect to, continuing the flow's direction. Reserve a clear right-hand column for yellow question and decision notes; stack active notes there and place answered notes below them or consolidate them into an answered-decisions note. Find free space from existing geometries before choosing `x`/`y`.
- **Grid:** snap to 10. Default shape 160×60 (decisions 160×80), 80 px gap along the flow, 60 px between parallel branches. Flow runs top to bottom unless the existing diagram runs left to right.
- If your additions came out cramped, tell the owner that **Arrange > Layout** (vertical flow) tidies the whole diagram in one click; whether to use it is their call.
- After editing, check the file is still well-formed XML: `python3 -c "import sys,xml.dom.minidom as m; m.parse(sys.argv[1])" <file>` (silent means good). draw.io also reports malformed XML when the owner opens the file.

## Flowchart vocabulary

Common style strings. Keep shapes uncoloured by default. When colour carries meaning (say, who does a step), use at most three fills and add a small legend note: bot/automated `fillColor=#dae8fc;strokeColor=#6c8ebf;`, human `fillColor=#f8cecc;strokeColor=#b85450;`, external system `fillColor=#d5e8d4;strokeColor=#82b366;`. Yellow is reserved for open-question notes.

| Meaning | Style |
| --- | --- |
| Step / action | `rounded=1;whiteSpace=wrap;html=1;` |
| Decision (yes/no) | `rhombus;whiteSpace=wrap;html=1;` |
| Start / end | `ellipse;whiteSpace=wrap;html=1;` |
| Input / output data | `shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;` |
| Stored data (DB) | `shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;size=15;` |
| External system / subprocess | `shape=process;whiteSpace=wrap;html=1;backgroundOutline=1;` |
| Human-in-the-loop | `shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;` (40×60) |
| Note / open question | `shape=note;whiteSpace=wrap;html=1;size=14;fillColor=#fff2cc;strokeColor=#d6b656;` |
| Group / lane (container) | `swimlane;whiteSpace=wrap;html=1;startSize=30;` children use `parent="<lane id>"` and coordinates relative to it |
| Arrow | `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;` |
| Dashed arrow (async / optional) | arrow style + `dashed=1;` |

Label decision branches on the edge (`value="yes"` / `value="no"`).

**Topic map:** the subject as an ellipse (200×80) near the centre of the page, e.g. `x=320 y=480`; branches as steps placed in a ring about 260 px out, each joined to the centre by a plain arrow with `endArrow=none;`. Sub-points sit a further 200 px out from their branch.

## Minimal complete example

Start → step → decision → two ends:

```xml
<mxfile host="drawio">
  <diagram id="page-1" name="Page-1">
    <mxGraphModel grid="1" gridSize="10" guides="1" connect="1" arrows="1" page="1" pageWidth="850" pageHeight="1100">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="start" value="Email arrives" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="320" y="40" width="160" height="60" as="geometry" />
        </mxCell>
        <mxCell id="step-classify" value="Classify request" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="320" y="180" width="160" height="60" as="geometry" />
        </mxCell>
        <mxCell id="dec-urgent" value="Urgent?" style="rhombus;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="320" y="320" width="160" height="80" as="geometry" />
        </mxCell>
        <mxCell id="end-page" value="Page on-call" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="100" y="480" width="160" height="60" as="geometry" />
        </mxCell>
        <mxCell id="end-queue" value="Add to queue" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="540" y="480" width="160" height="60" as="geometry" />
        </mxCell>
        <mxCell id="edge-start-classify" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="start" target="step-classify">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="edge-classify-urgent" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="step-classify" target="dec-urgent">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="edge-urgent-page" value="yes" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="dec-urgent" target="end-page">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="edge-urgent-queue" value="no" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="dec-urgent" target="end-queue">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```
