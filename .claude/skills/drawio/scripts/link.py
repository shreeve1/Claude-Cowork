#!/usr/bin/env python3
"""Print a link that opens a .drawio file in draw.io in the browser (app.diagrams.net).

Usage:
    python3 link.py <file.drawio>

The whole diagram travels in the link after "#", which the browser keeps to itself;
nothing is uploaded. Saving from that page is up to the owner (Save, Where: Device).
"""
import base64
import sys
import urllib.parse
import zlib
from pathlib import Path

APP = "https://app.diagrams.net/"
# Longer links may not open from a chat; give the file path instead.
MAX_LINK = 100_000


def link(path):
    xml = Path(path).read_text(encoding="utf-8-sig")
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    data = c.compress(urllib.parse.quote(xml, safe="").encode("ascii")) + c.flush()
    title = urllib.parse.quote(Path(path).name)
    return f"{APP}?title={title}#R" + urllib.parse.quote(base64.b64encode(data).decode("ascii"), safe="")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1 or not Path(argv[0]).is_file():
        print(__doc__, file=sys.stderr)
        return 2
    try:
        url = link(argv[0])
    except (OSError, UnicodeDecodeError) as e:
        print(f"cannot read {argv[0]}: {e}", file=sys.stderr)
        return 2
    if len(url) > MAX_LINK:
        print(f"link is {len(url)} characters, too long to click; give the file path instead", file=sys.stderr)
        return 1
    print(url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
