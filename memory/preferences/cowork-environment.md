---
title: Claude Cowork Environment
type: preference
status: promoted
created: 2026-10-10
updated: 2026-10-10
topics: [preference, workspace-layout, tools]
---

## Active memory

- This workspace runs only in Claude Cowork on Windows. It is a Claude-layout copy of the upstream Codex edition: `CLAUDE.md` replaces `AGENTS.md`, `.claude/` replaces `.agents/`. No `AGENTS.md` or `.agents/` may exist.
- Paths: file tools (`Read`, `Write`, `Edit`, `Glob`, `Grep`) use the Windows path `C:\Users\James\Documents\starter-agent-claude\...`. `Bash` runs in a Linux sandbox with the folder at `/sessions/<session>/mnt/starter-agent-claude/`; each call starts fresh, so begin with `cd /sessions/*/mnt/starter-agent-claude`. Never show `/sessions/...` paths to the user.
- Python is `python3` 3.10 in the sandbox; every shipped test suite passes on it, so the hooks accept 3.10 here. `python`/`py -3` in shipped docs means `python3` in the sandbox. Delete `__pycache__/` after running tests.
- Git: local repo, no remote, hooks at `.githooks`. Run every git command in the sandbox. Commit identity is set in the repo config.
- Skills: `.claude/skills/<name>/` is the one real copy. Cowork loads each through a loader skill saved to the account that reads `.claude/skills/<name>/SKILL.md` from the attached folder; loaders only work with this folder attached. A new skill gets a loader via `save_skill` (with the owner's OK): same name and description, body "Read `.claude/skills/<name>/SKILL.md` from the attached folder and follow it exactly. If it is not present, say so and stop."
- Tool names in shipped text: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `web_fetch`, `WebSearch`, `Agent` (subagents, including the "reviewer agent"), `AskUserQuestion`. Where a skill says to ask in plain text, do not use `AskUserQuestion`. `CODING_STANDARDS.md` does not exist in this edition: the reviewer checks the diff for correctness and minimal change.
- Updates: a new upstream Release is first converted with the `convert-release` skill, then `.claude/setup/UPDATE.md` is followed on the converted copy. Never copy upstream files in unconverted.
- `artifacts/migration/` holds the pre-conversion originals and the previous Claude workspace (migration Source). Exclude it from searches; never edit it.

## Notes

- Last reviewed: 2026-10-10
- Changed 2026-10-10: moved from the hand-edited `CLAUDE.md` into memory when Release 3 arrived, so shipped files stay exactly as converted.
