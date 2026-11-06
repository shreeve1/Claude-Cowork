"""Maintainer verification for the Cowork project-scaffolding port."""

import argparse
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEW_FILES = {
    "projects/README.md": "merge",
    "docs/testing/cowork-project-scaffolding-plan.md": "merge",
    "docs/testing/cowork-project-scaffolding-cases.md": "merge",
    "docs/testing/cowork-project-scaffolding-check.py": "merge",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh", action="store_true", help="Register new shipped files before build"
    )
    args = parser.parse_args()
    manifest_path = ROOT / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if args.refresh:
        for relative, kind in NEW_FILES.items():
            path = ROOT / relative
            manifest["files"][relative] = {
                "class": kind,
                "mode": "644",
                "sha256": hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
            }
        manifest_path.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
        print("Registered new Cowork project-scaffolding files; run the package build next.")
        return
    for relative, metadata in manifest["files"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        if actual != metadata["sha256"]:
            raise SystemExit(f"Manifest drift: {relative}")
    if (ROOT / "AGENTS.md").exists() or (ROOT / ".agents").exists():
        raise SystemExit("Unexpected upstream instruction layout")
    for relative in NEW_FILES:
        if relative not in manifest["files"]:
            raise SystemExit(f"New shipped file missing from manifest: {relative}")
    current = json.loads((ROOT / ".claude/cowork/skills/index.json").read_text(encoding="utf-8"))
    prior = subprocess.run(
        ["git", "show", "c033a99:.claude/cowork/skills/index.json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    previous = json.loads(prior)
    changed = {name for name, entry in current.items() if entry != previous.get(name)}
    if changed != {"personal-memory", "memory-setup"}:
        raise SystemExit(f"Unexpected changed skills: {sorted(changed)}")
    module_path = ROOT / ".claude/cowork/cowork_skills.py"
    spec = importlib.util.spec_from_file_location("cowork_packages", module_path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Cannot load Cowork package verifier: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="cowork previous ") as temporary:
        old = Path(temporary)
        index = old / ".claude/cowork/skills/index.json"
        index.parent.mkdir(parents=True)
        index.write_text(prior, encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = module.changed(ROOT, old, False)
        expected = [
            ".claude/cowork/skills/core/memory-setup.skill",
            ".claude/cowork/skills/core/personal-memory.skill",
        ]
        if result != 0 or output.getvalue().splitlines() != expected:
            raise SystemExit(f"Unexpected update cards: {output.getvalue()}")
    paths = [
        ROOT / ".claude/skills/personal-memory/hubs.py",
        ROOT / ".claude/skills/personal-memory/schema.py",
        ROOT / ".claude/skills/convert-release/scripts/convert_release.py",
        Path(__file__),
    ]
    paths += list((ROOT / ".claude/skills/personal-memory/tests").glob("test_*.py"))
    paths += list((ROOT / ".claude/skills/convert-release/tests").glob("test_*.py"))
    for path in paths:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=(3, 10))
    print(
        f"Verified {len(manifest['files'])} manifest hashes, two updated skill cards and Python 3.10 syntax."
    )


if __name__ == "__main__":
    main()
