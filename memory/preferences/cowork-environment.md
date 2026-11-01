---
title: Claude Cowork Environment
type: preference
status: promoted
created: 2026-10-10
updated: 2026-11-01
topics: [preference, workspace-layout, tools]
---

## Active memory

- This workspace runs in Claude Cowork on Windows. It is the Claude-layout edition of the starter workspace: `CLAUDE.md` and `.claude/`. No `AGENTS.md` or `.agents/` may exist.
- Paths: file tools (`Read`, `Write`, `Edit`, `Glob`, `Grep`) use the attached folder's Windows path. `Bash` runs in a Linux sandbox where the folder is mounted under `/sessions/<session>/mnt/<folder name>/`; each call starts fresh, so begin with `cd` into it. Never show `/sessions/...` paths to the owner.
- Python is `python3` in the sandbox (3.10 or newer; the shipped scripts support 3.10). `python`/`py -3` in shipped docs means `python3` in the sandbox. Delete `__pycache__/` after running tests.
- Git: hooks at `.githooks`. Run every git command in the sandbox. `.gitattributes` keeps files LF so the hooks run there.
- Linux checkout publishing: HTTPS Git and `gh` may have no login. The existing personal GitHub SSH identity authenticates as `shreeve1`; use its local key reference `~/.ssh/id_ed25519_github_personal` with `IdentitiesOnly=yes` and the SSH repo URL without changing `origin`. If host keys are absent, obtain GitHub’s public keys from `https://api.github.com/meta` over verified HTTPS and use a temporary known-hosts file with strict checking; never disable host verification. Push only with current approval.
- Skills: `.claude/skills/<name>/` is the source copy. Cowork uses the skills installed in the owner's own Cowork from the ready-made packages in `.claude/cowork/skills/core/` and `video/`: show the `.skill` files with `present_files` and the owner clicks **Save skill** on each card. Never build or zip skills for the owner; the packages ship with each version. If the owner edits a skill here, the installed copy does not change until they save an updated package.
- Installed skill paths: when `personal-memory` or `memory-setup` says `<skills>` or `~/.claude/skills`, use the verified parent of the actual skill folder in this session, not an assumed host path. In a starter workspace prefer its complete `.claude/skills/` copy. For another project, locate the installed Cowork copy and check `tasks.md`, `task-templates.md`, `supporting-templates.md` and `scaffold/` there before selecting it. Run helpers from the target workspace root. Task/proposal recovery follows `tasks.md`, not the memory-only `recovery.py`.
- Video skills installed: not asked yet
- Tool names in shipped text: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `web_fetch`, `WebSearch`, `Agent` (subagents, including the "reviewer agent"), `AskUserQuestion`. Where a skill says to ask in plain text, do not use `AskUserQuestion`. The reviewer checks a skill-script diff against `CODING_STANDARDS.md`.
- Setup source: for all three paths (first setup, migration, update), the owner downloads the workspace ZIP, adds it to the conversation, and pastes the matching numbered README prompt. Use the attached ZIP and its `.claude/setup/README.md`; do not fetch the source from GitHub. Owner testing found restricted systems need this attachment-based route.
- Updates keep the existing workspace folder, after a verified pre-update backup. Follow "A newer version arrived" in the attached ZIP’s guide; compare installed skill changes against that backup (`python3 .claude/cowork/cowork_skills.py changed "<backup folder>"`). Preserve personal content and stop for conflicts or failed checks.
- `artifacts/migration/` holds the previous workspace from an update. Exclude it from searches; never edit it.

## Notes

- Last reviewed: 2026-11-01
- Changed 2026-11-01: after testing a restricted system, owner requires a downloaded ZIP attached to the conversation for all three paths; same-folder updates remain unchanged.

## Related

- [Documents Go in Folders](memory/preferences/document-scaffolding.md) - owner document folders and project files survive updates.
