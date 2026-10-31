---
title: Claude Cowork Environment
type: preference
status: promoted
created: 2026-10-10
updated: 2026-10-27
topics: [preference, workspace-layout, tools]
---

## Active memory

- This workspace runs in Claude Cowork on Windows. It is the Claude-layout edition of the starter workspace: `CLAUDE.md` and `.claude/`. No `AGENTS.md` or `.agents/` may exist.
- Paths: file tools (`Read`, `Write`, `Edit`, `Glob`, `Grep`) use the attached folder's Windows path. `Bash` runs in a Linux sandbox where the folder is mounted under `/sessions/<session>/mnt/<folder name>/`; each call starts fresh, so begin with `cd` into it. Never show `/sessions/...` paths to the owner.
- Python is `python3` in the sandbox (3.10 or newer; the shipped scripts support 3.10). `python`/`py -3` in shipped docs means `python3` in the sandbox. Delete `__pycache__/` after running tests.
- Git: hooks at `.githooks`. Run every git command in the sandbox. `.gitattributes` keeps files LF so the hooks run there.
- Skills: `.claude/skills/<name>/` is the source copy. Cowork uses the skills installed in the owner's own Cowork from the ready-made packages in `.claude/cowork/skills/core/` and `video/`: show the `.skill` files with `present_files` and the owner clicks **Save skill** on each card. Never build or zip skills for the owner; the packages ship with each version. If the owner edits a skill here, the installed copy does not change until they save an updated package.
- Installed skill paths: when `personal-memory` or `memory-setup` says `<skills>` or `~/.claude/skills`, use the verified parent of the actual skill folder in this session, not an assumed host path. In a starter workspace prefer its complete `.claude/skills/` copy. For another project, locate the installed Cowork copy and check `tasks.md`, `task-templates.md`, `supporting-templates.md` and `scaffold/` there before selecting it. Run helpers from the target workspace root. Task/proposal recovery follows `tasks.md`, not the memory-only `recovery.py`.
- Video skills installed: not asked yet
- Tool names in shipped text: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `web_fetch`, `WebSearch`, `Agent` (subagents, including the "reviewer agent"), `AskUserQuestion`. Where a skill says to ask in plain text, do not use `AskUserQuestion`. The reviewer checks a skill-script diff against `CODING_STANDARDS.md`.
- Updates: a newer version is a new copy of this edition. Follow "A newer version arrived" in the new copy's `.claude/setup/README.md`; it shows cards only for new or changed skills (`python3 .claude/cowork/cowork_skills.py changed <old workspace>`).
- `artifacts/migration/` holds the previous workspace from an update. Exclude it from searches; never edit it.

## Notes

- Last reviewed: 2026-10-27
- Changed 2026-10-27: skills are installed into Cowork as `.skill` packages instead of loader skills; paths no longer name one owner's folder.
