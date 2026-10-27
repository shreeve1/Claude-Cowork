#!/usr/bin/env python3
"""Load memory/schema.json: the single Schema for subjects, topics, client dirs and the client folder name.

`load(memory_dir)` returns the schema dict. The file and its four keys are
required; a missing file or key exits with a clear one-line message naming the
path (and the key) instead of a traceback wall. `client_folder` is optional: the
name of the folder that holds Client Memory (`memory/<name>/`) and per-client
documents (`<name>/<short>/`); it defaults to `clients`.
"""

import json
import re
import sys
from pathlib import Path

REQUIRED_KEYS = ("client_subjects", "topics", "topic_dirs", "client_dirs")
DEFAULT_CLIENT_FOLDER = "clients"
RESERVED_FOLDERS = {
    "memory",
    "research",
    "reports",
    "notes",
    "artifacts",
    "tmp",
    "powershell",
    "preferences",
    "docs",
    "voice",
    "email",
    "guides",
    "workflows",
    "decisions",
    "candidates",
    "raw",
}


def load(memory_dir):
    path = Path(memory_dir) / "schema.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"Alert: memory schema file not found: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"Alert: memory schema file {path} is not valid JSON: {exc.msg}")
    if not isinstance(data, dict):
        sys.exit(f"Alert: memory schema file {path} must contain a JSON object")
    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        sys.exit(f"Alert: memory schema file {path} is missing key(s): {', '.join(missing)}")
    folder = data.setdefault("client_folder", DEFAULT_CLIENT_FOLDER)
    if (
        not isinstance(folder, str)
        or not re.fullmatch(r"[a-z][a-z0-9-]*", folder)
        or folder in RESERVED_FOLDERS
    ):
        sys.exit(
            f"Alert: memory schema file {path}: client_folder {folder!r} must be one lowercase word "
            f"(letters, digits, hyphen) that is not already a workspace or memory folder"
        )
    return data
