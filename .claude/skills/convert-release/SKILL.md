---
name: convert-release
description: Convert a new upstream Release of the starter-agent workspace (Codex layout - AGENTS.md, .agents/) into this workspace's Claude Cowork layout (CLAUDE.md, .claude/) before updating. Use when a newer Release arrives, the owner says "update my workspace", "I got a new version", or points at the upstream starter-agent folder.
---

# convert-release

Upstream Releases ship in the Codex layout, with a Codex adaptation on top. This workspace is the Claude layout. Every update converts first, then follows the shipped update steps on the converted copy.

## Steps

1. Ask the owner to attach the new upstream Release folder (and nothing else changes yet). Read its `CHANGELOG.md`, including any "Local changes" section; tell the owner in a few lines what changed.
2. In the Bash sandbox (paths per `memory/preferences/cowork-environment.md`), convert into a new scratch folder outside the workspace:
   `python3 .claude/skills/convert-release/scripts/convert_release.py <upstream release> /tmp/release-<N>-claude .`
   Read every line it prints:
   - "rule no longer matches upstream text": upstream changed a line a rule targets. Show the owner, update the rule in `scripts/convert_release.py`, rerun.
   - "warning: ... not in MANIFEST.json or EXTRA_FILES": a shipped file upstream forgot to list. Add it to `EXTRA_FILES` (or `DROP_FILES` if it belongs only to the upstream workspace) and rerun.
   - "check: ... still has Codex wording": add a `FILE_RULES` entry, or a `KEEP_WORKSPACE` entry when the whole upstream change is Codex adaptation, and rerun.
   - "check: upstream changed ..., which is kept from the workspace": read the upstream change, carry anything that is not Codex adaptation into the workspace copy, then update its `KEEP_WORKSPACE` sha256.
   Then build the ready-made Cowork packages in the converted copy: `python3 <converted>/.claude/cowork/cowork_skills.py build --workspace <converted>`. A "FAILED" line means Cowork would reject that skill: add a `FILE_RULES` entry (for example a `<` or `>` in a description) and rerun both steps. A new upstream skill that every owner needs goes into `CORE` in `cowork_skills.py`. Owners never build; they install these packages.
3. Check the converted copy: no `AGENTS.md` or `.agents/`; `grep -rn "\.agents\|AGENTS.md"` finds only the intended hits (`workflow-builder/agents-library` where AGENTS.md is a web standard, and `CHANGELOG.md`).
4. Follow "A newer version arrived" (and "Older Releases" when skipping a Release) in the converted copy's `.claude/setup/README.md`, with the converted copy as the new Release. Build the new workspace in a sandbox scratch folder and bring content across from this workspace. Copy this workspace whole (minus `.git` and `artifacts/migration/`) to `artifacts/migration/claude-workspace-r<old N>/` in the new workspace as the way back. Carry across this workspace's own files: `.claude/skills/convert-release/`, `memory/preferences/cowork-environment.md` and its `Always` row in `memory/rules.md`, and `README.md` (`.gitattributes`, `.claude/cowork/cowork_skills.py` and, after the build in step 2, the packages are already in the converted copy).
5. Verify in the scratch folder: `python3 .claude/skills/personal-memory/gate.py --memory memory audit` passes, the skill tests pass (`python3 -m unittest discover` in each skill's `tests/`), and step 3's grep is clean. Then show the owner the plan to replace this workspace's contents (keeping `.git` and `artifacts/`), and do it only with their OK. Commit (history kept) and verify again in place.
6. Update the skills in your Cowork as `.claude/setup/README.md` "Skills in the owner's app" says: `cowork_skills.py changed <the replaced workspace>`, show the listed packages, delete removed skills in Cowork's skill settings.

## Rules

- Never edit the upstream Release folder.
- Only mechanical rules go in the converter. Cowork-specific behaviour goes in `memory/preferences/cowork-environment.md`, never in a shipped file.
