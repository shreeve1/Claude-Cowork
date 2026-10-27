#!/usr/bin/env python3
"""Print a link that opens a .drawio file in draw.io in the browser (app.diagrams.net).

Usage:
    python3 link.py <file.drawio> [--html <preview.html>]

The whole diagram travels in the link after "#", which the browser keeps to itself;
nothing is uploaded. Saving from that page is up to the owner (Save, Where: Device).
--html also writes a preview page: the diagram in draw.io's viewer, with the edit link on top.
"""
import argparse
import base64
import html
import sys
import urllib.parse
import zlib
from pathlib import Path

APP = "https://app.diagrams.net/"
VIEWER = "https://viewer.diagrams.net/"
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
  iframe {{ flex: 1; border: 0; width: 100%; }}
</style></head>
<body>
<p><a href="{edit}" target="_blank" rel="noopener">Open in draw.io to edit</a> {title}</p>
<iframe src="{view}" title="{title}"></iframe>
</body></html>
"""


def payload(path):
    xml = Path(path).read_text(encoding="utf-8-sig")
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    data = c.compress(urllib.parse.quote(xml, safe="").encode("ascii")) + c.flush()
    return urllib.parse.quote(base64.b64encode(data).decode("ascii"), safe="")


def link(path, app=APP, extra=""):
    title = urllib.parse.quote(Path(path).name)
    return f"{app}?{extra}title={title}#R{payload(path)}"


def preview(path, out):
    edit, view = link(path), link(path, VIEWER, "lightbox=1&nav=1&edit=_blank&")
    title = html.escape(Path(path).name)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(PAGE.format(title=title, edit=html.escape(edit), view=html.escape(view)),
                         encoding="utf-8", newline="\n")


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
    print(url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
