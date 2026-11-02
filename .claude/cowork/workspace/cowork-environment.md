---
title: Claude Cowork Environment
type: preference
status: promoted
created: 2026-11-01
updated: 2026-11-01
topics: [preference, workspace-layout, tools]
---

Reference only for setup agents in staging. Do not copy or recreate this note in a new or migrated owner workspace; runtime helper resolution is in the generated `CLAUDE.md`. Existing owner notes are not permission for automatic deletion.

## Active memory

- This workspace is for Claude Cowork only. Maintainer skill sources, persona files, package-builder scripts and tests stay in the Release, not the owner’s workspace.
- Skills live in the owner’s Cowork installation. Setup presents ready-made `.skill` cards from the attached Release; the owner clicks **Save skill**. Source changes are not installation. Existing custom skills remain untouched.
- Find the actual installed personal-memory folder in this session. Verify readable `SKILL.md`, `tasks.md`, `task-templates.md`, `supporting-templates.md`, `reference.md`, needed `scaffold/` files and helper scripts before using it. Resolve `<skills>` as its actual parent folder; never substitute a maintainer checkout or assume a fixed install path. Keep this workspace attached.
- Memory, procedure and task helpers run from the installed personal-memory package, with the workspace as working directory. If Cowork does not expose its installed files or scripts, report the missing access and use only the skill’s documented manual checks. If exact recovery or safe containment cannot be verified, stop the affected edit.
- With Git and Python, the standalone pre-commit hook scans staged changes for secrets and audits relevant memory. After verifying installed personal-memory helpers, set `git config --local cowork.personalMemoryPath "<actual installed personal-memory folder>"`. This machine-local path must be rechecked after a session or machine change. The hook fails explicitly when a required audit is unavailable. Do not point it at an unverified folder or bypass it. Without Python, use only the message-length hook and disclose that automated secret/memory checks are off.
- File tools use the attached workspace’s visible path. Bash runs in Cowork’s sandbox; resolve the current mount rather than saving a session-specific mount in memory. Python is `python3` (3.10+). Show owner-visible paths, not temporary sandbox paths.
- First setup, migration and update all start with downloading the workspace ZIP and adding it to the conversation, then pasting the matching README prompt. Extract into separate staging; do not fetch GitHub or extract over owner content.
- Updates keep the workspace folder after a verified complete backup. Compare staged packages against `.claude/cowork/skills/index.json` in that backup, using the comparison helper from the attached Release. Present changed cards from staging; keep only the index here. Preserve personal files, memory, task history and custom skills.
- Video skills installed: not asked yet

## Notes

- Native Save skill and installed-folder access must be verified in the owner’s app; showing cards alone does not prove installation succeeded.
