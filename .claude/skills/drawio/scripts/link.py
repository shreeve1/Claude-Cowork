#!/usr/bin/env python3
"""Print a link that opens a .drawio file in draw.io in the browser (app.diagrams.net).

Usage:
    python3 link.py <file.drawio> [--html <preview.html>]

The whole diagram travels in the link after "#", which the browser keeps to itself;
nothing is uploaded. Saving from that page is up to the owner (Save, Where: Device).
--html also writes a preview page: a drawing of the first page, with the edit link on top.
The drawing is built in, so the page loads nothing from the internet.
"""
import argparse
import base64
import html
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

import svg

APP = "https://app.diagrams.net/"
# Longer links may not open from a chat; give the file path instead.
MAX_LINK = 100_000

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  html, body {{ margin: 0; height: 100%; font: 15px/1.4 system-ui, sans-serif; background: #fff; color: #1d1d1f; }}
  body {{ display: flex; flex-direction: column; }}
  p {{ margin: 0; padding: .6rem .75rem; border-bottom: 1px solid #ddd; }}
  a {{ color: #0b57d0; font-weight: 600; }}
  main {{ flex: 1; overflow: auto; padding: 1rem; }}
  main svg {{ max-width: 100%; height: auto; }}
  .note {{ color: #555; }}
</style></head>
<body>
<p><a href="{edit}" target="_blank" rel="noopener">Open in draw.io to edit</a> {title} <span class="note">{note}</span></p>
<main>{drawing}</main>
</body></html>
"""


def payload(path):
    xml = Path(path).read_text(encoding="utf-8-sig")
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    data = c.compress(urllib.parse.quote(xml, safe="").encode("ascii")) + c.flush()
    return urllib.parse.quote(base64.b64encode(data).decode("ascii"), safe="")


def link(path):
    return f"{APP}?title={urllib.parse.quote(Path(path).name)}#R{payload(path)}"


def preview(path, out):
    found = svg.pages(Path(path).read_text(encoding="utf-8-sig"))
    drawing = svg.svg(found[0][1]) if found else "<p>This diagram has no pages yet.</p>"
    note = f"(page {html.escape(found[0][0])}; {len(found) - 1} more in draw.io)" if len(found) > 1 else ""
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(PAGE.format(title=html.escape(Path(path).name), edit=html.escape(link(path)),
                                     note=note, drawing=drawing), encoding="utf-8", newline="\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file")
    ap.add_argument("--html", help="also write a preview page here")
    args = ap.parse_args(argv)
    if not Path(args.file).is_file():
        print(f"no such file: {args.file}", file=sys.stderr)
        return 2
    if args.html and (not args.html.endswith(".html") or Path(args.html).resolve() == Path(args.file).resolve()):
        print(f"--html must be a separate .html file: {args.html}", file=sys.stderr)
        return 2
    try:
        url = link(args.file)
        if len(url) > MAX_LINK:
            print(f"link is {len(url)} characters, too long to click; give the file path instead", file=sys.stderr)
            return 1
        if args.html:
            preview(args.file, args.html)
    except (OSError, UnicodeDecodeError) as e:
        print(f"cannot read {args.file}: {e}", file=sys.stderr)
        return 2
    except (ET.ParseError, zlib.error, ValueError) as e:
        print(f"cannot draw a preview of {args.file} (is it valid .drawio XML?): {e}", file=sys.stderr)
        print(url)
        return 1
    print(url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
