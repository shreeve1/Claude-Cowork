---
title: Pushing This Repo and Building Cowork Skill Packages
summary: Push via the github-personal SSH alias; rebuilding packages on Python 3.15 churns every .skill file without content change.
type: doc
status: promoted
created: 2026-11-14
updated: 2026-11-14
topics: [tools, git]
---

## Active memory

- "Push with my personal GitHub key" means the `github-personal` alias in `~/.ssh/config` (key `id_ed25519_github_personal`, port 443). The saved `origin` remote is HTTPS and uses Windows' saved login, so push by URL: `git push git@github-personal:shreeve1/Claude-Cowork.git main`, then `git fetch git@github-personal:shreeve1/Claude-Cowork.git main:refs/remotes/origin/main` to update tracking. (Verified 2026-11-14.)
- `python .claude/cowork/cowork_skills.py build` on this machine's Python 3.15 rewrites every `.skill` zip: file contents are identical, only zlib compression bytes differ, which also changes their MANIFEST.json hashes. `index.json` fingerprints are content-based and do not change. To add or change one skill, restore the untouched packages and re-hash MANIFEST, or package just that skill with `cowork_skills.package()`. (Verified 2026-11-14.)
- James's personal skills live in `~/.agents/skills/` (its own git repo). Copying one into Cowork's core list means adapting it: "James" becomes "the owner", and maintainer-only tools (herdr, codex handoff, independent-review) become reviewer subagents or the `handoff` skill. session-map was added this way on 2026-11-14.
