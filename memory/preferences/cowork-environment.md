---
title: Claude Cowork Environment
type: preference
status: promoted
created: 2026-10-10
updated: 2026-11-01
topics: [preference, workspace-layout, tools]
---

## Active memory

- This product is exclusively for Claude Cowork and always has been (owner clarification, 2026-11-01). Claude Code, Codex and other agent apps are not supported end-user targets; inherited multi-app instructions are drift, not an approved requirement. Maintainer tooling is separate from end-user installation. Use `CLAUDE.md` and `.claude/`; no `AGENTS.md` or `.agents/` may exist.
- Paths: file tools (`Read`, `Write`, `Edit`, `Glob`, `Grep`) use the attached folder's Windows path. `Bash` runs in a Linux sandbox where the folder is mounted under `/sessions/<session>/mnt/<folder name>/`; each call starts fresh, so begin with `cd` into it. Never show `/sessions/...` paths to the owner.
- Python is `python3` in the sandbox (3.10 or newer; the shipped scripts support 3.10). `python`/`py -3` in shipped docs means `python3` in the sandbox. Delete `__pycache__/` after running tests.
- Git: hooks at `.githooks`. Run every git command in the sandbox. `.gitattributes` keeps files LF so the hooks run there.
- Linux checkout publishing: HTTPS Git and `gh` may have no login. The existing personal GitHub SSH identity authenticates as `shreeve1`; use its local key reference `~/.ssh/id_ed25519_github_personal` with `IdentitiesOnly=yes` and the SSH repo URL without changing `origin`. If host keys are absent, obtain GitHub’s public keys from `https://api.github.com/meta` over verified HTTPS and use a temporary known-hosts file with strict checking; never disable host verification. Push only with current approval.
- Skills: `.claude/skills/` is maintainer source only. Fresh user workspaces exclude it, persona libraries, builders, tests and `.skill` archives. Present ready-made packages from the attached Release’s `.claude/cowork/skills/core/` and optional `video/`; the owner clicks **Save skill** in Cowork. Keep only the package index in the user workspace. Preserve existing custom skills and legacy sources unless specific removal is approved. Never build or zip skills for an end user.
- Installed skill paths: resolve personal-memory’s actual Cowork-installed folder each session; verify task/templates, scaffold and helpers there. Daily work never depends on a maintainer source copy. Run helpers from the target workspace root. Task/proposal recovery follows `tasks.md`, not memory-only `recovery.py`. A Git memory hook uses verified local `cowork.personalMemoryPath`; recheck it after session changes. Missing access blocks affected operations except documented manual checks. This maintainer checkout may run its own source helpers.
- Windows Claude viewing from `wrk` (verified 2026-11-01): invoke `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe` from Linux. Discover the current Claude window handle with `Get-Process`; handles are temporary. UI Automation exposed only window chrome, not chat text. `System.Drawing` plus `user32.dll` `PrintWindow(handle, dc, 2)` produced a readable screenshot of only the Claude window in Windows `%TEMP%`; read it through `/mnt/c/Users/...`. Use literal shell quoting or PowerShell here-strings, not shell-expanded `$_` or C-style quote escapes. No desktop MCP connector was available in this session. View requests do not authorize clicks, typing or changes.
- Video skills installed: not asked yet
- Tool names in shipped text: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `web_fetch`, `WebSearch`, `Agent` (subagents, including the "reviewer agent"), `AskUserQuestion`. Where a skill says to ask in plain text, do not use `AskUserQuestion`. The reviewer checks a skill-script diff against `CODING_STANDARDS.md`.
- Setup source: for all three paths (first setup, migration, update), the owner downloads the workspace ZIP, adds it to the conversation, and pastes the matching numbered README prompt. Use the attached ZIP and its `.claude/setup/README.md`; do not fetch the source from GitHub. Owner testing found restricted systems need this attachment-based route.
- Updates keep the existing workspace folder, after a verified pre-update backup. Follow "A newer version arrived" in the attached ZIP’s guide; run the comparison helper from the extracted Release against that backup, not from the user workspace. Preserve personal content and stop for conflicts or failed checks.
- Guided end-user experience (owner clarification, 2026-11-01): applies to every step of setup, migration and updates, not just backup selection. Claude handles routine technical work and gives concrete next actions, exact visible button labels and what to expect whenever the user must act. Avoid technical-choice questionnaires; ask for genuine personalization/adaptation decisions and required permissions/approvals. For backup access, guide folder selection toward Documents, validate suitability, explain the backup subfolder versus unchanged workspace, and confirm the backup location before copying. Documents is a recommendation, not assumed safe or accessible.
- `artifacts/migration/` holds the previous workspace from an update. Exclude it from searches; never edit it.

## Notes

- Last reviewed: 2026-11-01
- Changed 2026-11-01: owner confirmed Cowork-only scope and approved separating maintainer sources from user workspaces; attached ZIPs and verified same-folder updates remain required.

## Related

- [Documents Go in Folders](memory/preferences/document-scaffolding.md) - owner document folders and project files survive updates.
