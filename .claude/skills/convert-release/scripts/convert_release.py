#!/usr/bin/env python3
"""Convert an upstream Release (Codex layout: AGENTS.md, .agents/) into this workspace's
Claude Cowork layout (CLAUDE.md, .claude/).

Usage (from the workspace root, in the Cowork Bash sandbox):
    python3 .claude/skills/convert-release/scripts/convert_release.py <release_dir> <out_dir> <workspace_dir>

Writes a converted copy to <out_dir> (must not exist) with a fresh MANIFEST.json whose
sha256 values match the converted files. Files in KEEP_WORKSPACE are copied from
<workspace_dir> instead of upstream. The original Release is never modified.
Only mechanical, repeatable rules live here. Cowork-specific rules are not shipped files:
they live in memory (`memory/preferences/cowork-environment.md`).
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

# Codex-only files dropped from the converted Release.
DROP_SUFFIXES = ("/agents/openai.yaml",)

# Upstream files that belong to the upstream workspace, not to a Release. Never copied.
DROP_FILES = (
    ".agents/setup/CODEX.md",
    "memory/decisions/projects/decision-github-repository.md",
    "memory/decisions/workstation/decision-codex-workspace.md",
    "memory/docs/it-client-subjects.md",
)

# Upstream files shipped but missing from upstream MANIFEST.json, with their class.
# Any other unlisted upstream file is reported so a rule can be added here.
EXTRA_FILES = {
    "CODING_STANDARDS.md": "merge",
    ".agents/skills/meeting/SKILL.md": "merge",
    ".agents/skills/meeting/scripts/meetings.py": "merge",
    ".agents/skills/meeting/scripts/tests/test_meetings.py": "merge",
    "memory/preferences/meetings.md": "seed",
    "memory/preferences/memory-maintenance.md": "seed",
}

# Upstream rewrote these for Codex only. Keep this workspace's copy (converted path), pinned to
# the upstream MANIFEST sha256 that was reviewed; a different upstream sha is reported.
KEEP_WORKSPACE = {
    ".claude/skills/adhd/SKILL.md": "06debe68a370206acd93e0b2ee54d6395bc367fdfbc079f2348e3ce2966dac0a",
    ".claude/skills/brainstorm-idea/SKILL.md": "c7ef5024075d4a48c56f034b810370ef38294b8677700f7b778d48efaaab4f2e",
    ".claude/skills/excalidraw-diagram/SKILL.md": "13ab4e81bac89f5651374cb5f3413cab8dcd5d5667e990391418d8fb888989da",
    ".claude/skills/teach/SKILL.md": "cf6d1bf8276a7a01fb97a720402f3452eb69ad90b573a2488684808e51091f76",
}

# Shipped files that exist only in this edition; copied from the workspace into every conversion.
WORKSPACE_ONLY = {
    ".gitattributes": {"class": "merge", "mode": "644"},
    ".claude/setup/cowork_skills.py": {"class": "merge", "mode": "755"},
}

TEXT_EXT = (".md", ".py", ".json", ".txt", ".html", ".toml", ".yaml", ".ps1", ".sh", ".gitignore")

# Files where AGENTS.md is a real web standard, not this workspace's instructions file.
KEEP_AGENTS_MD = (".claude/skills/workflow-builder/agents-library/",)

TEXT_RULES = [
    (".agents/skills", ".claude/skills"),
    (".agents\\skills", ".claude\\skills"),
    (".agents/", ".claude/"),
    (".agents\\", ".claude\\"),
    ('".agents"', '".claude"'),
    ("(`.agents`, `.githooks`)", "(`.claude`, `.githooks`)"),
    ("Call the `read` tool on", "Call `Read` on"),
    ("Never use the `question` tool", "Never use the `AskUserQuestion` tool"),
    ("No `question` tool", "No `AskUserQuestion` tool"),
    ("use `question` when", "use `AskUserQuestion` when"),
    ("use `question` with", "use `AskUserQuestion` with"),
    ("Use `read`, `glob`, `grep`, and limited `bash`", "Use `Read`, `Glob`, `Grep`, and limited `Bash`"),
    ("Use `task` subagents", "Use `Agent` subagents"),
    ("use `task` subagents", "use `Agent` subagents"),
    ("Use `webfetch`", "Use `web_fetch`"),
    ("Use `read` for directories when possible. Use `bash`",
     "Use `Glob` (or `ls` via Bash) for directories. Use `Bash`"),
    ("Use `glob` and `grep`", "Use `Glob` and `Grep`"),
    ("then `read` the `memory/preferences/` directory",
     "then list the `memory/preferences/` directory (Glob `memory/preferences/*.md`)"),
]

# Replaces upstream's Cowork loader step in setup/README.md: Cowork gets real skills.
COWORK_SKILLS_STEP = """\
- **Claude Cowork** loads skills only from the owner's own Cowork, so install them there. Ask once: "Install this workspace's skills into your Cowork? I'll show a card for each skill and you click **Save skill** on each." On a yes:
  1. First setup only, ask once: "Do you also want the video skills (about 27, some large)?" The core skills are always installed.
  2. In the Bash sandbox, from the new workspace: `python3 .claude/setup/cowork_skills.py package artifacts/skills` (add `--video` on a yes). It checks each skill against Cowork's upload rules, zips it into `artifacts/skills/<name>.skill` and records what it packaged in `.claude/cowork-skills.json`.
  3. Show every `.skill` file it lists in one `present_files` call. Tell the owner to click **Save skill** on each card, and that a card without that button means their organisation does not allow adding skills: they ask their admin, then you show the cards again.
  4. For each `FAILED <name>` line, tell the owner that skill was not installed and why.

  On an update, add `--previous <old workspace>`, the folder being replaced, never the new one. It keeps the old video choice and packages only skills that are new or changed. For each `removed: <name>` line, tell the owner to delete that skill in Cowork's skill settings. If it prints `loaders: yes`, the old setup used loader skills: saving the new cards replaces them, and any other old loader the owner did not get a card for (for example video skills) should be deleted in Cowork's skill settings. Leave the owner's own skills alone. Tell the owner the skills read and write this workspace, so keep this folder attached in Cowork.
"""

# Per-file rules, applied after TEXT_RULES and the AGENTS.md rename. Each strips upstream's
# Codex adaptation; a rule that stops matching means upstream changed that text.
FILE_RULES = {
    "CLAUDE.md": [
        ("1. Read `memory/index.md`, `memory/glossary.md` and `memory/rules.md` with the available file or "
         "shell tools (in Codex on Windows, `Get-Content -LiteralPath`; a tool named `read` is not required).",
         "1. Call `Read` on `memory/index.md`, `memory/glossary.md` and `memory/rules.md`."),
        (re.compile(r"## Codex runtime\n.*?\n\n+(?=## )", re.S), ""),
        (" They are not enabled in this Codex workspace; run those checks directly before commits.", ""),
    ],
    ".claude/setup/README.md": [
        (" A short `CLAUDE.md` that only says \"Read CLAUDE.md\" is fine when the owner's app needs one.", ""),
        ("Using Codex on Windows, with hooks skipped: `CODEX.md`.\n\n", ""),
        (re.compile(r"- \*\*Claude Cowork\*\* and any app that loads skills only from its own saved list:.*?\n(?=- \*\*Another app:\*\*)",
                    re.S), COWORK_SKILLS_STEP),
        ("7. Keep the old `.git` folder only if the owner wants the history;",
         "7. Update the skills in the owner's app (\"Skills in the owner's app\" above, with `--previous`).\n"
         "8. Keep the old `.git` folder only if the owner wants the history;"),
    ],
    ".claude/setup/ADAPTING.md": [
        (re.compile(r"Codex reads `CLAUDE\.md` and `\.claude/skills/` directly\..*?\n\n", re.S), ""),
        ("some read another file name (for example `CLAUDE.md`)", "some read another file name (for example `AGENTS.md`)"),
        ("this is the loader step in `README.md`", "this is the install step in `README.md`"),
    ],
    ".claude/skills/memory-setup/SKILL.md": [
        ("In Claude Cowork, an existing `personal-memory` skill loader works when this folder is attached, "
         "so save one only if none exists.",
         "In Claude Cowork, use the `personal-memory` skill installed in the owner's Cowork; if it is missing, "
         "zip `<skills>/personal-memory/` into `personal-memory.skill` (the folder at the zip root) and present "
         "it with `present_files` so the owner can click Save skill."),
    ],
    ".claude/skills/personal-memory/scaffold/AGENTS-memory.md": [
        ("into the project's CLAUDE.md or CLAUDE.md,", "into the project's CLAUDE.md,"),
    ],
    # Cowork's skill upload rejects angle brackets in a description.
    ".claude/skills/hyperframes-audio/SKILL.md": [
        ("for several tracks at once (`<hf-audio-group>`).", "for several tracks at once (an `hf-audio-group` element)."),
    ],
    ".claude/skills/startday-spec/references/adaptation-list.md": [
        (re.compile(r"   In Codex, use the available automation tools.*?shell loop\.\n\n", re.S), ""),
    ],
    ".claude/skills/youtube/SKILL.md": [
        ("Use when the user says `/youtube <url>`,", "Use when the user says `/youtube` with a URL,"),
        (re.compile(r"In Codex, use the supplied OS and shell context first\..*?into shell code\.\n\n", re.S), ""),
        ("   - Prefer built-in web search for background research; use a connected read-only search tool if needed.\n"
         "   - Use the available web page-open tool for known, reachable URLs.",
         "   - Prefer this workspace's browser search when search results are needed.\n"
         "   - Use `web_fetch` for direct URL fetches when URL is known and reachable."),
    ],
    "memory/README.md": [
        (" Shipped hooks are disabled in this Codex workspace; run the memory audit directly before committing.", ""),
        ("; this workspace's does: [GitHub repository](memory/decisions/projects/decision-github-repository.md).", "."),
    ],
    "memory/rules.md": [
        (re.compile(r"\| Updating this workspace to a new Release \| \| `memory/decisions/workstation/"
                    r"decision-codex-workspace\.md` \|[^\n]*\n"), ""),
    ],
    "memory/index.md": [
        (re.compile(r"\| \[IT Client Subjects\]\(memory/docs/it-client-subjects\.md\) \|[^\n]*\n"), ""),
    ],
    "memory/decisions/index.md": [
        (re.compile(r"- \[Starter-agent GitHub repository\][^\n]*\n"), ""),
        (re.compile(r"- \[Codex workspace with hooks skipped\][^\n]*\n"), ""),
    ],
}

# Generated indexes whose sections may be left empty by FILE_RULES; empty sections are dropped.
DROP_EMPTY_SECTIONS = ("memory/decisions/index.md",)

# Codex wording that should not survive conversion outside third-party skills.
CODEX_MARKERS = ("Codex collaboration", "fork_turns", "In Codex,", "Codex workspace",
                 "in Codex on Windows", "CODEX.md", "decision-codex-workspace")
CODEX_OK = (".claude/skills/hyperframes", "CHANGELOG.md")


def new_path(rel):
    if rel == "AGENTS.md":
        return "CLAUDE.md"
    if rel.startswith(".agents/"):
        return ".claude/" + rel[len(".agents/"):]
    return rel


def is_text(rel, data):
    if b"\0" in data[:8192]:
        return False
    name = rel.rsplit("/", 1)[-1]
    return rel.endswith(TEXT_EXT) or "." not in name or rel.startswith(".githooks/")


def convert_text(rel, text):
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")
    for a, b in TEXT_RULES:
        text = text.replace(a, b)
    if not rel.startswith(KEEP_AGENTS_MD):
        text = text.replace("AGENTS.md", "CLAUDE.md").replace("AGENTS\\.md", "CLAUDE\\.md")
    for a, b in FILE_RULES.get(rel, []):
        if isinstance(a, re.Pattern):
            text, n = a.subn(b, text)
        else:
            n = text.count(a)
            text = text.replace(a, b)
        if not n:
            pat = a.pattern if isinstance(a, re.Pattern) else a
            raise SystemExit(f"{rel}: rule no longer matches upstream text: {pat[:80]!r}; update convert_release.py")
    if rel in DROP_EMPTY_SECTIONS:
        text = drop_empty_sections(text)
    return text.replace("\n", "\r\n") if crlf else text


def drop_empty_sections(text):
    """Remove `## ` headings with no lines before the next heading or the end."""
    text = re.sub(r"\n## [^\n]+\n\s*(?=\n## |\Z)", "", text)
    return text.rstrip("\n") + "\n"


def sha(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def upstream_files(src):
    return {p.relative_to(src).as_posix() for p in src.rglob("*")
            if p.is_file() and not {".git", "__pycache__"} & set(p.relative_to(src).parts)}


def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    src, out, ws = (Path(a).resolve() for a in argv)
    mpath = src / "MANIFEST.json"
    if not mpath.is_file():
        print(f"{src} has no MANIFEST.json", file=sys.stderr)
        return 2
    if out.exists():
        print(f"{out} already exists; pick a new folder", file=sys.stderr)
        return 2
    missing = [rel for rel in ("CLAUDE.md", *KEEP_WORKSPACE, *WORKSPACE_ONLY) if not (ws / rel).is_file()]
    if missing:
        print(f"{ws} is not this workspace (missing {', '.join(missing)})", file=sys.stderr)
        return 2
    tmp = out.with_name(out.name + ".partial")
    if tmp.exists():
        shutil.rmtree(tmp)
    try:
        convert(src, mpath, tmp, ws)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    tmp.rename(out)
    print(f"-> {out}")
    return 0


def convert(src, mpath, out, ws):
    man = json.loads(mpath.read_text(encoding="utf-8"))
    entries = dict(man["files"])
    for rel, cls in EXTRA_FILES.items():
        if rel in entries:
            print(f"note: {rel} is now in upstream MANIFEST.json; remove it from EXTRA_FILES")
        elif (src / rel).is_file():
            entries[rel] = {"class": cls, "mode": "755" if rel.endswith(".py") and "/tests/" not in rel else "644"}
        else:
            print(f"note: EXTRA_FILES entry {rel} not in this Release")
    unlisted = upstream_files(src) - set(entries) - set(DROP_FILES) - {"MANIFEST.json"}
    for rel in sorted(unlisted):
        print(f"warning: {rel} is in the Release but not in MANIFEST.json or EXTRA_FILES; not copied")

    files, flagged = {}, []
    for rel, meta in entries.items():
        if rel.endswith(DROP_SUFFIXES) or rel in DROP_FILES:
            continue
        nrel = new_path(rel)
        if nrel in KEEP_WORKSPACE:
            if "sha256" in meta and meta["sha256"] != KEEP_WORKSPACE[nrel]:
                print(f"check: upstream changed {rel}, which is kept from the workspace; "
                      f"review the upstream change, then update its KEEP_WORKSPACE sha256")
            data = (ws / nrel).read_bytes()
        else:
            data = (src / rel).read_bytes()
            if is_text(nrel, data):
                data = convert_text(nrel, data.decode("utf-8")).encode("utf-8")
        if is_text(nrel, data) and not nrel.startswith(CODEX_OK):
            text = data.decode("utf-8", "replace")
            if any(m in text for m in CODEX_MARKERS):
                flagged.append(nrel)
        dest = out / nrel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        mode = meta.get("mode")
        if mode:
            dest.chmod(int(mode, 8))
        files[nrel] = dict(meta, sha256=sha(data))
    for rel, meta in WORKSPACE_ONLY.items():
        if rel in files:
            raise SystemExit(f"{rel} now ships upstream; remove it from WORKSPACE_ONLY")
        data = (ws / rel).read_bytes()
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        dest.chmod(int(meta["mode"], 8))
        files[rel] = dict(meta, sha256=sha(data))
    man["files"] = dict(sorted(files.items()))
    (out / "MANIFEST.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    print(f"converted {len(files)} files")
    for rel in flagged:
        print(f"check: {rel} still has Codex wording; add a FILE_RULE or a KEEP_WORKSPACE entry")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
