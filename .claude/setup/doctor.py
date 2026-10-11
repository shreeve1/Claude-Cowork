#!/usr/bin/env python3
"""Read-only check of this workspace. Changes nothing.

    python .claude/setup/doctor.py              everyday check
    python .claude/setup/doctor.py --migration  the setup gate: INSTALL.md and UPDATE.md are not done until it passes

Run from the workspace root. Prints one line per check; exit 1 means something needs fixing. `doctor.ps1` runs the
same structure and ledger checks on Windows computers without Python. The rules are listed in MIGRATING.md,
"What the check enforces".
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MIN_PY = (3, 10)
ROOT = Path.cwd()
LEDGER = "memory/migration-ledger.md"
OUTCOMES = {"moved", "merged", "dropped", "none"}
OLD_LAYOUT = {".opencode", "opencode.jsonc", ".agents", "AGENTS.md"}
ROOT_EXTRA_FILES = {"MANIFEST.json", ".gitignore", ".mcp.json", ".DS_Store", "Thumbs.db", "1.Activity.md"}
ROOT_EXTRA_DIRS = {".git", ".claude", ".codex"}
POINTERS = {"GEMINI.md"}
SKIP = {".git", "node_modules", "__pycache__", ".venv", ".DS_Store", "Thumbs.db"}
problems = 0


def report(ok, label, fix=""):
    global problems
    problems += not ok
    print(("ok    " if ok else "FIX   ") + label + ("" if ok or not fix else f"\n      -> {fix}"))


def info(text):
    print("info  " + text)


def run(*cmd):
    try:
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    except OSError:
        return None


def sha_lf(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def norm(p):
    return p.strip().replace("\\", "/").removeprefix("./").strip("/") if p else ""


def tools(strict):
    report(True, f"python {sys.version.split()[0]}")
    p3 = run("python3", "-c", "import sys; print(sys.version_info >= (3, 10), sys.version.split()[0])")
    hooks_python = p3 is not None and p3.returncode == 0 and p3.stdout.startswith("True")
    git = bool(shutil.which("git"))
    if not git:
        info("git not found: no version history and no commit checks (the workspace still works)")
        return False
    inside = run("git", "rev-parse", "--is-inside-work-tree")
    repo = inside is not None and inside.stdout.strip() == "true"
    report(repo, "workspace has its own git history", "run `git init` here (INSTALL.md)")
    if not repo:
        return False
    publish = run("git", "config", "--local", "--get", "hooks.publishRelease")
    report(not (publish and publish.stdout.strip() == "true"), "this is a workspace, not the Release repo itself",
           "copy the Release into a new folder and work there (INSTALL.md)")
    if strict:
        remotes = run("git", "remote")
        report(not (remotes and remotes.stdout.strip()), "no remote copied from the Release",
               "this folder was cloned: copy its files without .git into a new folder (INSTALL.md)")
    if (ROOT / ".githooks").is_dir():
        hp = run("git", "config", "core.hooksPath")
        path = hp.stdout.strip() if hp is not None else ""
        if hooks_python:
            report(path == ".githooks", "git hooks switched on (secret scan, memory check, push protection)",
                   "run `git config core.hooksPath .githooks`")
        else:
            info("python3 3.10+ not found: the secret scan and memory check cannot run")
            report(path == ".githooks/nopython", "push protection switched on without Python",
                   "run `git config core.hooksPath .githooks/nopython`; never leave the hooks off")
    return repo


def manifest():
    m = ROOT / "MANIFEST.json"
    if not m.is_file():
        report(False, "MANIFEST.json present", "this folder is not a copy of a Release (INSTALL.md)")
        return {}
    return json.loads(m.read_text(encoding="utf-8")).get("files", {})


def shipped(files, strict):
    missing = sorted(p for p in files if not (ROOT / p).is_file())
    changed = sorted(p for p, m in files.items() if m["class"] == "merge" and (ROOT / p).is_file()
                     and sha_lf(ROOT / p) != m["sha256"])
    if strict:
        report(not missing, "every shipped file is present",
               "restore from the Release: " + ", ".join(missing[:8]) + (" ..." if len(missing) > 8 else ""))
        report(not changed, "shipped files arrive unchanged",
               "restore from the Release; personal rules go to memory (MIGRATING.md): " + ", ".join(changed[:8]))
    else:
        if missing:
            info(f"{len(missing)} shipped file(s) removed by the owner, e.g. {missing[0]}")
        if changed:
            info(f"{len(changed)} shipped file(s) edited by the owner, e.g. {changed[0]}")


def folder_map():
    doc = ROOT / "memory/preferences/document-scaffolding.md"
    return set(re.findall(r"`([A-Za-z0-9._-]+)/", doc.read_text(encoding="utf-8"))) if doc.is_file() else set()


def layout(files):
    top_files = {p for p in files if "/" not in p}
    top_dirs = {p.split("/")[0] for p in files if "/" in p} | folder_map() | ROOT_EXTRA_DIRS
    bad = []
    for child in sorted(ROOT.iterdir()):
        name = child.name
        if name in OLD_LAYOUT:
            bad.append(f"{name} (old layout: move what it holds per MIGRATING.md, then delete it)")
        elif child.is_dir() and name not in top_dirs:
            bad.append(f"{name}/ (not in the folder map memory/preferences/document-scaffolding.md)")
        elif child.is_file() and name in POINTERS:
            text = child.read_text(encoding="utf-8", errors="replace")
            if "CLAUDE.md" not in text or len([l for l in text.splitlines() if l.strip()]) > 10:
                bad.append(f"{name} (only a short pointer to CLAUDE.md is allowed)")
        elif child.is_file() and name not in top_files | ROOT_EXTRA_FILES:
            bad.append(f"{name} (no loose files in the root; see the folder map)")
    report(not bad, "workspace root matches the shipped layout", "; ".join(bad))
    skills = ROOT / ".claude/skills"
    broken = sorted(d.name for d in skills.iterdir() if d.is_dir() and not (d / "SKILL.md").is_file()) \
        if skills.is_dir() else []
    report(not broken, "every skill folder has a SKILL.md", ", ".join(broken))


def parse_ledger(text):
    sources = [s.strip() for s in re.findall(r"^Source:\s*(.+)$", text, re.M)]
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.lstrip().startswith("|") or len(cells) < 4 or cells[0] == "Source" or set(line) <= set("|-: "):
            continue
        rows.append(cells[:4])
    return sources, rows


def source_files(src):
    base = Path(src)
    if base.is_file():
        return [base.name]
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        out += [(Path(dirpath) / f).relative_to(base).as_posix() for f in filenames if f not in SKIP]
    return out


def ledger(files, strict):
    path = ROOT / LEDGER
    if not path.is_file():
        report(not strict, "migration ledger present", f"write {LEDGER} (MIGRATING.md, step 1)")
        return
    sources, rows = parse_ledger(path.read_text(encoding="utf-8"))
    merge_files = {p for p, m in files.items() if m["class"] == "merge"}
    bad = []
    if not rows:
        bad.append("no rows; a workspace with nothing to migrate has one row with outcome `none`")
    if any(r[2] == "none" for r in rows) and len(rows) > 1:
        bad.append("`none` must be the only row")
    for src, dest, outcome, note in rows:
        if outcome not in OUTCOMES:
            bad.append(f"{src}: outcome `{outcome}` is not one of {', '.join(sorted(OUTCOMES))}")
        elif outcome == "dropped" and not note:
            bad.append(f"{src}: dropped needs a reason in Note")
        elif outcome in ("moved", "merged"):
            for d in filter(None, (norm(x.split("#")[0]) for x in dest.split(","))):
                if not (ROOT / d).exists():
                    bad.append(f"{src}: destination {d} does not exist")
                elif d in merge_files:
                    bad.append(f"{src}: {d} is a shipped file; personal content goes to memory or your own skill")
                elif d.split("/")[0] in OLD_LAYOUT:
                    bad.append(f"{src}: {d} is old layout")
            if not dest.strip():
                bad.append(f"{src}: {outcome} needs a Destination")
    for s in sources:
        if not Path(s).exists():
            bad.append(f"Source {s} cannot be read here (attach or copy it, then rerun)")
            continue
        base = norm(s)
        listed = [norm(r[0])[len(base):].strip("/") if norm(r[0]).lower().startswith(base.lower()) else norm(r[0])
                  for r in rows]
        listed = [l + "/" if r[0].rstrip().endswith(("/", "\\")) else l for l, r in zip(listed, rows)]
        missed = [f for f in source_files(s) if not any(f == l or (l.endswith("/") and f.startswith(l)) for l in listed)]
        if missed:
            bad.append(f"Source {s}: {len(missed)} file(s) have no row, e.g. " + ", ".join(missed[:5]))
    if strict and not sources and not any(r[2] == "none" for r in rows):
        bad.append("no `Source:` line: list every old folder or file migrated from")
    report(not bad, "migration ledger complete", "\n      -> ".join(bad[:15]))
    dropped = [r for r in rows if r[2] == "dropped"]
    if dropped:
        info(f"{len(dropped)} item(s) dropped; the owner must have agreed to each (see {LEDGER})")


def memory_audit():
    gate = ROOT / ".claude/skills/personal-memory/gate.py"
    if gate.is_file():
        au = run(sys.executable, str(gate), "--memory", "memory", "audit")
        out = (au.stdout + au.stderr).strip().splitlines() if au else ["could not run"]
        report(au is not None and au.returncode == 0, "memory audit passes",
               "\n      ".join(out[:8]) + "\n      (the commit check runs this audit; fix what it lists)")


def team(repo):
    if not (ROOT / ".claude/skills/startday/scripts/operator_profile.py").is_file():
        return
    sys.path.insert(0, str(ROOT / ".claude/skills/startday/scripts"))
    try:
        import operator_profile
        prof = operator_profile.load(ROOT)
    except SystemExit as e:
        report(False, "Operator Profile loads", f"{e} (OPERATOR-PROFILE.md)")
        return
    report(True, f"Operator Profile loads ({prof.name}, {prof.tz.key})")
    mcp = ROOT / ".mcp.json"
    try:
        servers = json.loads(mcp.read_text(encoding="utf-8")).get("mcpServers", {}) if mcp.is_file() else {}
    except json.JSONDecodeError:
        servers = {}
    entry = servers.get(prof.mcp_server)
    usable = isinstance(entry, dict) and bool(entry.get("url")) \
        and isinstance(entry.get("headers"), dict) and bool(entry["headers"].get("Authorization"))
    report(usable, f".mcp.json has the `{prof.mcp_server}` server startday uses, with a url and token",
           "write .mcp.json (INSTALL.md) with `url` and `headers.Authorization`; it holds your own token")
    if repo:
        ignored = run("git", "check-ignore", "-q", ".mcp.json")
        report(ignored is not None and ignored.returncode == 0, ".mcp.json is git-ignored",
               "it holds your token: add the line `.mcp.json` to .gitignore before writing it")
        tracked = run("git", "ls-files", "--error-unmatch", ".mcp.json")
        report(tracked is not None and tracked.returncode != 0, ".mcp.json is not committed",
               "it holds a token: `git rm --cached .mcp.json` and keep it in .gitignore")


def main():
    sys.dont_write_bytecode = True
    if sys.version_info < MIN_PY:
        print(f"FIX   this Python is {sys.version.split()[0]}; 3.10 or newer is needed, or run doctor.ps1.")
        return 1
    strict = "--migration" in sys.argv[1:]
    repo = tools(strict)
    files = manifest()
    if files:
        shipped(files, strict)
        layout(files)
    ledger(files, strict)
    memory_audit()
    team(repo)
    print("\nAll checks passed." if not problems else f"\n{problems} thing(s) to fix.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
