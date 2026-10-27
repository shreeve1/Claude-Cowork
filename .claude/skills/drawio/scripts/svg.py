"""Draw the first page of a .drawio file as a self-contained SVG, for a preview.

An approximation of what draw.io shows: common shapes, labels, colours and arrows.
It loads nothing from the internet, so it shows where external pages are blocked.
"""
import base64
import html
import re
import urllib.parse
import xml.etree.ElementTree as ET
import zlib

MARGIN = 20
CHAR_W = 7  # rough width of one character at 12px, for wrapping
COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}|[a-zA-Z]+")


def pages(xml):
    """Return [(name, mxGraphModel element)] for every page; compressed pages are decoded."""
    root = ET.fromstring(xml)
    if root.tag == "mxGraphModel":
        return [("Page-1", root)]
    out = []
    for d in root.iter("diagram"):
        model = d.find("mxGraphModel")
        if model is None and (d.text or "").strip():
            raw = zlib.decompress(base64.b64decode(d.text.strip()), -15).decode("utf-8", "replace")
            model = ET.fromstring(urllib.parse.unquote(raw))
        if model is not None:
            out.append((d.get("name") or f"Page-{len(out) + 1}", model))
    return out


def style_of(cell):
    s = {}
    for i, part in enumerate((cell.get("style") or "").split(";")):
        if "=" in part:
            k, v = part.split("=", 1)
            s[k] = v
        elif part:
            s.setdefault("shape" if i == 0 else part, part)
    return s


def label_lines(value, width):
    text = re.sub(r"<br\s*/?>|</(div|p)>", "\n", value or "", flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    per_line = max(4, int(width // CHAR_W))
    lines = []
    for para in text.split("\n"):
        words, line = para.split(), ""
        for w in words:
            if line and len(line) + 1 + len(w) > per_line:
                lines.append(line)
                line = w
            else:
                line = f"{line} {w}".strip()
        lines.append(line)
    while lines and not lines[-1]:
        lines.pop()
    return lines


def text_svg(lines, cx, cy, color="#1d1d1f", size=12):
    if not lines:
        return ""
    top = cy - (len(lines) - 1) * size * 0.6
    spans = "".join(f'<tspan x="{cx:.1f}" y="{top + i * size * 1.2:.1f}">{html.escape(l)}</tspan>'
                    for i, l in enumerate(lines))
    return (f'<text text-anchor="middle" dominant-baseline="middle" font-family="Helvetica, Arial, sans-serif" '
            f'font-size="{size}" fill="{html.escape(color)}">{spans}</text>')


def num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def colour(s, key, default):
    v = s.get(key, default)
    if v in ("none", ""):
        return "none"
    return v if v != "default" and COLOUR.fullmatch(v) else default


def shape_svg(s, x, y, w, h):
    fill, stroke = colour(s, "fillColor", "#ffffff"), colour(s, "strokeColor", "#1d1d1f")
    paint = f'fill="{html.escape(fill)}" stroke="{html.escape(stroke)}" stroke-width="1.2"'
    if s.get("dashed") == "1":
        paint += ' stroke-dasharray="5 4"'
    kind = s.get("shape", "")
    if kind == "text" or "text" in s:
        return ""
    if kind in ("ellipse", "doubleEllipse"):
        return f'<ellipse cx="{x + w / 2}" cy="{y + h / 2}" rx="{w / 2}" ry="{h / 2}" {paint}/>'
    if kind == "rhombus":
        return f'<polygon points="{x + w / 2},{y} {x + w},{y + h / 2} {x + w / 2},{y + h} {x},{y + h / 2}" {paint}/>'
    if kind == "parallelogram":
        d = min(20, w / 4)
        return f'<polygon points="{x + d},{y} {x + w},{y} {x + w - d},{y + h} {x},{y + h}" {paint}/>'
    if kind == "cylinder3":
        r = min(15, h / 4)
        return (f'<path d="M{x},{y + r} A{w / 2},{r} 0 0 1 {x + w},{y + r} V{y + h - r} '
                f'A{w / 2},{r} 0 0 1 {x},{y + h - r} Z M{x},{y + r} A{w / 2},{r} 0 0 0 {x + w},{y + r}" {paint}/>')
    if kind == "note":
        f = min(14, w / 4, h / 4)
        return f'<polygon points="{x},{y} {x + w - f},{y} {x + w},{y + f} {x + w},{y + h} {x},{y + h}" {paint}/>'
    if kind == "umlActor":
        cx = x + w / 2
        return (f'<g {paint} fill="none"><circle cx="{cx}" cy="{y + h * 0.15}" r="{h * 0.15}"/>'
                f'<path d="M{cx},{y + h * 0.3} V{y + h * 0.65} M{x},{y + h * 0.42} H{x + w} '
                f'M{cx},{y + h * 0.65} L{x},{y + h} M{cx},{y + h * 0.65} L{x + w},{y + h}"/></g>')
    if kind == "swimlane":
        head = num(s.get("startSize"), 30)
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" {paint}/>'
                f'<line x1="{x}" y1="{y + head}" x2="{x + w}" y2="{y + head}" stroke="{html.escape(stroke)}"/>')
    if kind == "process":
        d = min(12, w / 8)
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" {paint}/>'
                f'<path d="M{x + d},{y} V{y + h} M{x + w - d},{y} V{y + h}" stroke="{html.escape(stroke)}"/>')
    rx = min(10, w / 6, h / 6) if s.get("rounded") == "1" else 0
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" {paint}/>'


def clip(box, px, py):
    """Point where the line from the box centre towards (px, py) leaves the box."""
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    dx, dy = px - cx, py - cy
    if dx == 0 and dy == 0:
        return cx, cy
    t = min(w / 2 / abs(dx) if dx else float("inf"), h / 2 / abs(dy) if dy else float("inf"))
    return cx + dx * t, cy + dy * t


def svg(model):
    cells = {}
    for el in model.iter():
        if el.tag in ("UserObject", "object"):  # draw.io wraps cells that have custom properties
            inner = el.find("mxCell")
            if inner is not None and el.get("id") is not None:
                inner.set("id", el.get("id"))
                inner.set("value", el.get("label", ""))
                cells[el.get("id")] = inner
        elif el.tag == "mxCell" and el.get("id") is not None:
            cells[el.get("id")] = el
    boxes, parts, edges = {}, [], []

    def origin(cid, seen=()):
        c = cells.get(cid)
        if c is None or c.get("vertex") != "1" or cid in seen:
            return 0.0, 0.0
        g = c.find("mxGeometry")
        ox, oy = origin(c.get("parent"), (*seen, cid))
        return ox + num(g.get("x", 0)) if g is not None else ox, oy + num(g.get("y", 0)) if g is not None else oy

    for c in cells.values():
        g = c.find("mxGeometry")
        parent = cells.get(c.get("parent"))
        on_edge = parent is not None and parent.get("edge") == "1"
        if c.get("vertex") == "1" and g is not None and g.get("relative") != "1" and not on_edge:
            ox, oy = origin(c.get("parent"))
            boxes[c.get("id")] = (ox + num(g.get("x", 0)), oy + num(g.get("y", 0)),
                                  num(g.get("width", 0)), num(g.get("height", 0)))
        elif c.get("edge") == "1":
            edges.append(c)

    for c in cells.values():
        box = boxes.get(c.get("id"))
        if box is None:
            continue
        s = style_of(c)
        x, y, w, h = box
        parts.append(shape_svg(s, x, y, w, h))
        below = s.get("verticalLabelPosition") == "bottom"
        lines = label_lines(c.get("value"), max(w, 120) if below else w)
        color = colour(s, "fontColor", "#1d1d1f")
        if s.get("shape") == "swimlane":
            parts.append(text_svg(lines, x + w / 2, y + num(s.get("startSize"), 30) / 2, color))
        elif below:
            parts.append(text_svg(lines, x + w / 2, y + h + 6 + len(lines) * 7, color))
        else:
            parts.append(text_svg(lines, x + w / 2, y + h / 2, color))

    for e in edges:
        s, g = style_of(e), e.find("mxGeometry")
        pts = [(num(p.get("x", 0)), num(p.get("y", 0))) for p in g.iter("mxPoint")
               if p.get("as") is None] if g is not None else []
        ends = {p.get("as"): (num(p.get("x", 0)), num(p.get("y", 0)))
                for p in (g.iter("mxPoint") if g is not None else []) if p.get("as")}
        src, dst = boxes.get(e.get("source")), boxes.get(e.get("target"))
        a = (src[0] + src[2] / 2, src[1] + src[3] / 2) if src else ends.get("sourcePoint")
        b = (dst[0] + dst[2] / 2, dst[1] + dst[3] / 2) if dst else ends.get("targetPoint")
        if a is None or b is None:
            continue
        mid = list(pts)
        if not mid and "orthogonalEdgeStyle" in s.get("edgeStyle", "") and abs(a[0] - b[0]) > 1 and abs(a[1] - b[1]) > 1:
            mid = [(b[0], a[1])]
        first, last = (mid[0] if mid else b), (mid[-1] if mid else a)
        if src:
            a = clip(src, *first)
        if dst:
            b = clip(dst, *last)
        path = [a, *mid, b]
        stroke = html.escape(colour(s, "strokeColor", "#1d1d1f"))
        dash = ' stroke-dasharray="5 4"' if s.get("dashed") == "1" else ""
        arrow = "" if s.get("endArrow") == "none" else ' marker-end="url(#arrow)"'
        d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in path)
        parts.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="1.2"{dash}{arrow}/>')
        lines = label_lines(e.get("value"), 120)
        if lines:
            i = len(path) // 2
            (x1, y1), (x2, y2) = path[i - 1], path[i]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            w = max(len(l) for l in lines) * CHAR_W + 6
            parts.append(f'<rect x="{mx - w / 2:.1f}" y="{my - 8 * len(lines):.1f}" width="{w:.1f}" '
                         f'height="{16 * len(lines)}" fill="#ffffff"/>')
            parts.append(text_svg(lines, mx, my, size=11))

    xs = [v for x, y, w, h in boxes.values() for v in (x, x + w)] or [0, 100]
    ys = [v for x, y, w, h in boxes.values() for v in (y, y + h + 24)] or [0, 100]
    x0, y0 = min(xs) - MARGIN, min(ys) - MARGIN
    width, height = max(xs) - x0 + MARGIN, max(ys) - y0 + MARGIN
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.0f} {y0:.0f} {width:.0f} {height:.0f}" '
            f'width="{width:.0f}" height="{height:.0f}" role="img">'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#1d1d1f"/></marker></defs>'
            + "".join(parts) + "</svg>")
