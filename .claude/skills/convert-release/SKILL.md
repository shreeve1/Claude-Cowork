---
name: convert-release
description: Convert a new upstream Release of the starter-agent workspace (Codex layout - AGENTS.md, .agents/) into this workspace's Claude Cowork layout (CLAUDE.md, .claude/) before updating. Use when a newer Release arrives, the owner says "update my workspace", "I got a new version", or points at the upstream starter-agent folder.
---

# convert-release

Upstream Releases ship in the Codex layout. This workspace is the Claude layout. Every update converts first, then follows the shipped update procedure on the converted copy.

## Steps

1. Ask the owner to attach the new upstream Release folder (and nothing else changes yet). Read its `CHANGELOG.md`; tell the owner in a few lines what changed.
2. In the Bash sandbox (paths per `memory/preferences/cowork-environment.md`), convert into a new scratch folder outside the workspace:
   `python3 .claude/skills/convert-release/scripts/convert_release.py <upstream release> /tmp/release-<N>-claude`
   If it stops with "rule no longer matches upstream text", upstream changed a line a rule targets: show the owner, update the rule in `scripts/convert_release.py`, rerun.
3. Check the converted copy: no `AGENTS.md` or `.agents/`; `grep -rn "\.agents\|AGENTS.md"` finds only the intended hits (`workflow-builder/agents-library` where AGENTS.md is a web standard).
4. Follow `.claude/setup/UPDATE.md` with the converted copy as the new Release, building the new workspace in a sandbox scratch folder and migrating from this workspace. Copy this workspace whole (minus `.git` and `artifacts/migration/`) to `artifacts/migration/claude-workspace-r<old N>/` in the new workspace and use that as the ledger `Source:`. This skill is the owner's own skill: copy `.claude/skills/convert-release/` across whole.
5. When every item under "What must be true" in `.claude/setup/MIGRATING.md` is verified in the scratch folder, show the owner the plan to replace this workspace's contents (keeping `.git` and `artifacts/`), and do it only with their OK. Then commit (`UPDATE.md` step 4: history kept) and verify again in place.
6. Update Cowork loader skills: new skills get a loader, removed skills' loaders are overwritten to say they are retired, changed descriptions are re-saved.

## Rules

- Never edit the upstream Release folder.
- Only mechanical rules go in the converter. Cowork-specific behaviour goes in `memory/preferences/cowork-environment.md`, never in a shipped file.
