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
    "docs/superpowers/plans/2026-10-30-procedure-first-memory.md",
    "docs/superpowers/plans/2026-10-31-workspace-tasks.md",
    "docs/superpowers/plans/2026-11-01-flexible-workspace-setup.md",
    "docs/superpowers/specs/2026-10-30-procedure-first-memory-design.md",
    "docs/superpowers/specs/2026-10-31-workspace-supporting-templates.md",
    "docs/superpowers/specs/2026-10-31-workspace-tasks-design.md",
    "docs/superpowers/specs/2026-10-31-workspace-tasks-templates.md",
)
DROP_DIRS = {".git", "__pycache__", ".memory-recovery", ".task-recovery",
             ".pi", ".pytest_cache", ".ruff_cache"}

# Upstream files shipped but missing from upstream MANIFEST.json, with their class.
# Any other unlisted upstream file is reported so a rule can be added here.
EXTRA_FILES = {
    "CODING_STANDARDS.md": "merge",
    ".agents/skills/meeting/SKILL.md": "merge",
    ".agents/skills/meeting/scripts/meetings.py": "merge",
    ".agents/skills/meeting/scripts/tests/test_meetings.py": "merge",
    "memory/preferences/meetings.md": "seed",
    "memory/preferences/memory-maintenance.md": "seed",
    "memory/preferences/talk-it-through.md": "seed",
    ".agents/skills/personal-memory/procedures.py": "merge",
    ".agents/skills/personal-memory/recovery.py": "merge",
    ".agents/skills/personal-memory/supporting-templates.md": "merge",
    ".agents/skills/personal-memory/task-templates.md": "merge",
    ".agents/skills/personal-memory/tasks.md": "merge",
    ".agents/skills/personal-memory/tests/test_policy.py": "merge",
    ".agents/skills/personal-memory/tests/test_procedures.py": "merge",
    ".agents/skills/personal-memory/tests/test_recovery.py": "merge",
    ".agents/skills/personal-memory/tests/test_tasks_policy.py": "merge",
    "docs/testing/procedure-first-memory-cases.md": "merge",
    "docs/testing/workspace-tasks-cases.md": "merge",
    "docs/testing/flexible-workspace-setup-cases.md": "merge",
    "projects/README.md": "merge",
    "tasks/index.md": "seed",
}

# Keep this workspace's Claude versions, pinned to reviewed upstream source bytes.
# The upstream manifest may predate local changes, so it cannot detect drift here.
KEEP_WORKSPACE = {
    ".claude/skills/adhd/SKILL.md": "2f8bd439ba0ad1a3c470dc68431ec5b4c7f8d4ba226110e4b409f14579316a03",
    ".claude/skills/brainstorm-idea/SKILL.md": "140ffb06d0136d762c8183e6e09e19c994dd185433c32dedcfe4e3d38d3cce49",
    ".claude/skills/excalidraw-diagram/SKILL.md": "440ccc5be5a9beb83586374f79755ddee6c42f2c3814ad95e9c3ac4eb7feace1",
    ".claude/skills/teach/SKILL.md": "ef48fefe3bf0315ec615f7a3d3a36e4d41f67eb3d52d5a8fbd1ee8316013f602",
}

# Upstream skill folders replaced by this edition's own version (its files are in WORKSPACE_ONLY),
# pinned to a hash of the upstream folder that was reviewed; a different upstream folder is reported.
REPLACED_DIRS = {
    ".agents/skills/drawio/": "5343e9e34ae9ee2981968600c142bae192fd78397cc4cc2d0fd2717e864b3c70",
}

# Shipped files that exist only in this edition; copied from the workspace into every conversion.
WORKSPACE_ONLY = {
    "README.md": {"class": "merge", "mode": "644"},
    "memory/preferences/cowork-environment.md": {"class": "seed", "mode": "644"},
    ".gitattributes": {"class": "merge", "mode": "644"},
    ".claude/cowork/cowork_skills.py": {"class": "merge", "mode": "755"},
    ".claude/cowork/workspace.py": {"class": "merge", "mode": "755"},
    ".claude/cowork/workspace/CLAUDE.md": {"class": "merge", "mode": "644"},
    ".claude/cowork/workspace/cowork-environment.md": {"class": "merge", "mode": "644"},
    ".claude/setup/README.md": {"class": "merge", "mode": "644"},
    ".claude/setup/ADAPTING.md": {"class": "merge", "mode": "644"},
    ".claude/setup/WEEKLY-SWEEP.md": {"class": "merge", "mode": "644"},
    ".claude/setup/MANIFEST.md": {"class": "merge", "mode": "644"},
    ".claude/skills/memory-setup/SKILL.md": {"class": "merge", "mode": "644"},
    ".claude/skills/personal-memory/SKILL.md": {"class": "merge", "mode": "644"},
    ".claude/skills/drawio/SKILL.md": {"class": "merge", "mode": "644"},
    ".claude/skills/drawio/reference/format.md": {"class": "merge", "mode": "644"},
    ".claude/skills/drawio/scripts/link.py": {"class": "merge", "mode": "755"},
    ".claude/skills/drawio/scripts/tests/test_link.py": {"class": "merge", "mode": "644"},
    ".claude/skills/drawio/scripts/svg.py": {"class": "merge", "mode": "644"},
    ".claude/skills/drawio/scripts/tests/test_svg.py": {"class": "merge", "mode": "644"},
}

EDITION_OWNED = {".claude/skills/memory-setup/SKILL.md", ".claude/skills/personal-memory/SKILL.md",
                 ".claude/setup/README.md", ".claude/setup/ADAPTING.md",
                 ".claude/setup/WEEKLY-SWEEP.md", ".claude/setup/MANIFEST.md"}

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

# Per-file rules, applied after TEXT_RULES and the AGENTS.md rename. Each strips upstream's
# Codex adaptation; a rule that stops matching means upstream changed that text.
FILE_RULES = {
    "CLAUDE.md": [
        (re.compile(r"## Codex runtime\n.*?\n\n+(?=## )", re.S), ""),
        (" They are not enabled in this Codex workspace; run those checks directly before commits.", ""),
    ],
    "START-HERE.md": [
        ("Git and Python 3.11+ add version history", "Git and Python 3.10+ add version history"),
        ("Your AI agent (Claude Cowork or Codex) sets it up", "Your AI agent in Claude Cowork sets it up"),
        ("- Claude Cowork or Codex.", "- Claude Cowork on Windows."),
        ("decides where things belong and tells you what it did.\n",
         "decides where things belong and tells you what it did. Then it shows a card for each skill: "
         "click **Save skill** on each to install it. Video skills are optional.\n"),
    ],
    ".githooks/nopython/commit-msg": [
        ("without Python 3.11+", "without Python 3.10+"),
    ],
    ".claude/skills/personal-memory/SKILL.md": [
        ("saved workspace tasks: create, look up, continue, review, complete or archive a task.",
         "saved workspace tasks (create, look up, continue, review, complete or archive a task)."),
    ],
    ".claude/skills/personal-memory/task-templates.md": [
        (re.compile(r"\n+\Z"), "\n"),
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
    # The upstream author's own skill paths; in Cowork the draw.io canvas is the visual companion.
    ".claude/skills/talk-it-through/SKILL.md": [
        ("If accepted, read `visual-companion.md` from the installed superpowers brainstorming skill directory. "
         "In this workspace that is `/home/james/.pi/agent/git/github.com/obra/superpowers/skills/brainstorming/visual-companion.md`. "
         "If it is unavailable,",
         "If accepted and the picture is a flow, structure or map, use the `drawio` skill. Otherwise read "
         "`visual-companion.md` from the installed superpowers brainstorming skill, if there is one. If it is unavailable,"),
        (" In this workspace that is `/home/james/.pi/agent/git/github.com/obra/superpowers/skills/brainstorming/builder-check-prompt.md`.",
         ""),
    ],
    ".claude/skills/youtube/SKILL.md": [
        ("Use when the user says `/youtube <url>`,", "Use when the user says `/youtube` with a URL,"),
        (re.compile(r"In Codex, use the supplied OS and shell context first\..*?into shell code\.\n\n", re.S), ""),
        ("   - Prefer built-in web search for background research; use a connected read-only search tool if needed.\n"
         "   - Use the available web page-open tool for known, reachable URLs.",
         "   - Prefer this workspace's browser search when search results are needed.\n"
         "   - Use `web_fetch` for direct URL fetches when URL is known and reachable."),
    ],
    "projects/README.md": [
        ("`.claude/skills/personal-memory/supporting-templates.md`",
         "`supporting-templates.md` beside the verified Cowork-installed personal-memory skill"),
    ],
    "memory/preferences/document-scaffolding.md": [
        ("`.claude/skills/personal-memory/supporting-templates.md`",
         "`supporting-templates.md` beside the verified Cowork-installed personal-memory skill"),
    ],
    "memory/README.md": [
        (" Shipped hooks are disabled in this Codex workspace; run the memory audit directly before committing.", ""),
        ("; this workspace's does: [GitHub repository](memory/decisions/projects/decision-github-repository.md).", "."),
    ],
    "memory/rules.md": [
        ("| Always | | `tasks/index.md` | Optional; skip absence without creating files. |",
         "| Always | | `tasks/index.md` | Optional; skip absence without creating files. |\n"
         "| Always | | `memory/preferences/cowork-environment.md` | |"),
        (re.compile(r"\| Updating this workspace to a new Release \| \| `memory/decisions/workstation/"
                    r"decision-codex-workspace\.md` \|[^\n]*\n"), ""),
    ],
    "memory/index.md": [
        ("| [Workflows Index](memory/workflows/index.md) | index | Workflows by topic; generated by `indexes.py`. | |",
         "| [Workflows Index](memory/workflows/index.md) | index | Workflows by topic; generated by `indexes.py`. | |\n"
         "| [Claude Cowork Environment](memory/preferences/cowork-environment.md) | preference | "
         "Cowork paths, sandbox Python, git, installing skills as .skill packages, update flow. | 2026-10-27 |"),
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
CODEX_OK = (".claude/skills/hyperframes", "CHANGELOG.md", "docs/testing/")


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
    # Historical test receipts must retain the paths and clients actually tested.
    if rel.startswith("docs/testing/"):
        return text
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


def tree_sha(src, rels):
    h = hashlib.sha256()
    for rel in sorted(rels):
        h.update(rel.encode() + b"\0" + sha((src / rel).read_bytes()).encode() + b"\0")
    return h.hexdigest()


def upstream_files(src):
    return {p.relative_to(src).as_posix() for p in src.rglob("*")
            if p.is_file() and not DROP_DIRS & set(p.relative_to(src).parts)}


def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    src, out, ws = (Path(a).resolve() for a in argv)
    mpath = src / "MANIFEST.json"
    if not mpath.is_file():
        print(f"{src} has no MANIFEST.json", file=sys.stderr)
        return 2
    if out.is_relative_to(src) or out.is_relative_to(ws):
        print("output must be outside the source and workspace", file=sys.stderr)
        return 2
    if out.exists():
        print(f"{out} already exists; pick a new folder", file=sys.stderr)
        return 2
    missing = [rel for rel in ("CLAUDE.md", *KEEP_WORKSPACE, *WORKSPACE_ONLY) if not (ws / rel).is_file()]
    if missing:
        print(f"{ws} is not this workspace (missing {', '.join(missing)})", file=sys.stderr)
        return 2
    tmp = out.with_name(out.name + ".partial")
    if tmp.exists() or tmp.is_symlink():
        print(f"{tmp} already exists; preserve it and pick a new output", file=sys.stderr)
        return 2
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
    present = upstream_files(src)
    replaced = set()
    for folder, pinned in REPLACED_DIRS.items():
        rels = {rel for rel in present if rel.startswith(folder)}
        if rels and tree_sha(src, rels) != pinned:
            print(f"check: upstream changed {folder}, which this workspace replaces; port what applies "
                  f"to its WORKSPACE_ONLY files, then update its REPLACED_DIRS hash")
        elif not rels:
            print(f"note: {folder} not in this Release; remove it from REPLACED_DIRS if upstream dropped it")
        replaced |= rels
    entries = {rel: meta for rel, meta in entries.items() if rel not in replaced}
    unlisted = present - replaced - set(entries) - set(DROP_FILES) - {"MANIFEST.json"}
    for rel in sorted(unlisted):
        print(f"warning: {rel} is in the Release but not in MANIFEST.json or EXTRA_FILES; not copied")

    files, flagged = {}, []
    for rel, meta in entries.items():
        if rel.endswith(DROP_SUFFIXES) or rel in DROP_FILES or DROP_DIRS & set(Path(rel).parts):
            continue
        nrel = new_path(rel)
        if nrel in EDITION_OWNED:
            print(f"check: review upstream changes to {rel}; using the Cowork-owned version")
            continue
        if nrel in KEEP_WORKSPACE:
            if sha((src / rel).read_bytes()) != KEEP_WORKSPACE[nrel]:
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
