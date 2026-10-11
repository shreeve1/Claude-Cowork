#!/usr/bin/env python3
r"""Serve a local Excalidraw editor URL for a .excalidraw scene.

    Usage, macOS/Linux shell:
    cd .claude/skills/excalidraw-diagram/scripts
    uv run python export_to_excalidraw_url.py ../../../../artifacts/diagrams/example.excalidraw --port 0
    # or without uv:
    # . .venv/bin/activate && python export_to_excalidraw_url.py ../../../../artifacts/diagrams/example.excalidraw --port 0

    Usage, Windows PowerShell:
    cd .claude\skills\excalidraw-diagram\scripts
    uv run python export_to_excalidraw_url.py ..\..\..\..\artifacts\diagrams\example.excalidraw --port 0
    # or without uv:
    # .\.venv\Scripts\Activate.ps1; python export_to_excalidraw_url.py ..\..\..\..\artifacts\diagrams\example.excalidraw --port 0
"""

from __future__ import annotations

import argparse
import json
import socketserver
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler
from pathlib import Path

HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Excalidraw Local Export</title>
  <link rel=\"stylesheet\" href=\"https://esm.sh/@excalidraw/excalidraw@0.18.0/dist/dev/index.css\" />
  <style>
    html, body, #app {{ height: 100%; margin: 0; }}
    body {{ font-family: Inter, system-ui, sans-serif; }}
    .topbar {{
      position: fixed; top: 12px; left: 12px; z-index: 10;
      background: rgba(255,255,255,.92); border: 1px solid #dbe4f0; border-radius: 10px;
      padding: 10px 12px; box-shadow: 0 6px 20px rgba(0,0,0,.08);
      font-size: 13px; color: #334155;
    }}
    .topbar code {{ font-size: 12px; }}
  </style>
  <script>window.EXCALIDRAW_ASSET_PATH = \"https://esm.sh/@excalidraw/excalidraw@0.18.0/dist/prod/\";</script>
  <script type=\"importmap\">{{
    \"imports\": {{
      \"react\": \"https://esm.sh/react@19.0.0\",
      \"react/jsx-runtime\": \"https://esm.sh/react@19.0.0/jsx-runtime\",
      \"react-dom\": \"https://esm.sh/react-dom@19.0.0\"
    }}
  }}</script>
</head>
<body>
  <div class=\"topbar\">Loaded: <code>{scene_name}</code><br/>Local Excalidraw editor URL.</div>
  <div id=\"app\"></div>
  <script type=\"module\">
    import * as ExcalidrawLib from 'https://esm.sh/@excalidraw/excalidraw@0.18.0/dist/dev/index.js?external=react,react-dom';
    import React from 'https://esm.sh/react@19.0.0';
    import {{ createRoot }} from 'https://esm.sh/react-dom@19.0.0/client';

    const scene = await fetch('/scene').then((r) => r.json());

    function App() {{
      return React.createElement('div', {{ style: {{ height: '100%' }} }},
        React.createElement(ExcalidrawLib.Excalidraw, {{
          initialData: scene,
          UIOptions: {{
            canvasActions: {{
              loadScene: true,
              saveToActiveFile: true,
              export: true,
              saveAsImage: true,
            }}
          }}
        }})
      );
    }}

    createRoot(document.getElementById('app')).render(React.createElement(App));
  </script>
</body>
</html>
"""


def validate_scene(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("type") != "excalidraw":
        raise ValueError("input is not an Excalidraw scene")
    if not isinstance(data.get("elements"), list):
        raise ValueError("scene missing elements array")
    return data


class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class Handler(BaseHTTPRequestHandler):
    scene_data: bytes = b"{}"
    scene_name: str = "scene.excalidraw"

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            html = HTML_TEMPLATE.format(scene_name=self.scene_name).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        if self.path == "/scene":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(self.scene_data)))
            self.end_headers()
            self.wfile.write(self.scene_data)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve a local Excalidraw URL for a scene")
    parser.add_argument("input", type=Path, help="Path to .excalidraw scene")
    parser.add_argument("--port", type=int, default=0, help="Port to bind; 0 picks available port")
    parser.add_argument("--open", action="store_true", help="Open system browser automatically")
    parser.add_argument("--url-file", type=Path, help="Write selected local URL to this file")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        data = validate_scene(args.input)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    Handler.scene_data = json.dumps(data).encode("utf-8")
    Handler.scene_name = args.input.name

    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as httpd:
        url = f"http://127.0.0.1:{httpd.server_address[1]}"
        if args.url_file:
            args.url_file.parent.mkdir(parents=True, exist_ok=True)
            args.url_file.write_text(url + "\n", encoding="utf-8")
        print(url, flush=True)
        if args.open:
            webbrowser.open(url)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            thread.join()
        except KeyboardInterrupt:
            httpd.shutdown()


if __name__ == "__main__":
    main()
