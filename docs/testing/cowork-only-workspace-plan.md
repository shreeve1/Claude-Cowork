# Cowork-only workspace implementation plan

## Approved scope

Claude Cowork is the sole end-user target. The owner approved separating maintainer sources from the user workspace, installing ready-made Cowork packages, removing other-app setup branches, and preserving memory, saved tasks and safe same-folder updates. All three entry paths use an attached ZIP.

## Implementation

1. Add regression tests for a filtered user workspace: no shipped skill sources, persona files, maintainer scripts or packaged skill archive copies. Keep user memory, tasks, project scaffolding, a package index for future comparisons, and standalone Git safety hooks. Validate paths, refuse nonempty destinations, and preserve source files. Test the real copied workspace without the maintainer source tree.
2. Add a small standard-library workspace file selector/copier under `.claude/cowork/`; setup uses it only for first creation, while updates use its projected manifest for an approved file plan, not a bulk overwrite. Keep source and installed skills separate. Run package comparison from the extracted ZIP without requiring `.claude/skills`.
3. Supply Cowork-only workspace instructions and an environment seed. Resolve personal-memory helpers/templates from the installed package, never a maintainer path. Let the standalone pre-commit hook use a verified machine-local installed personal-memory path; a required unavailable audit fails explicitly, never silently passes. Test missing and installed helper cases.
4. Rewrite setup/adaptation/sweep entry points for Cowork only, installed skills, preservation of legacy source/user skills, normalized text comparisons, backup-before-replacement, and no committing unrelated staged work. Update memory-setup and maintainer conversion so regeneration retains the Cowork-specific setup files. Rebuild only changed packages and refresh manifests.
5. Run targeted tests and direct copied-workspace probes, all repository unit suites, memory audit and manifest checks. Have a read-only reviewer check the diff against CODING_STANDARDS.md, fix findings, then commit exact paths. Do not push.

## Acceptance checks

- Fresh user workspace contains no `.claude/skills/`, no persona source tree and no `.skill` archive copies; ready-made cards come from the attached Release.
- Installed personal-memory supplies task templates, recovery and audit tools; no broken source-tree references are introduced into copied runtime instructions.
- Same-folder update compares package index from backup against staged packages; owner skills and uncommitted documents are preserved.
- CRLF-only differences are not personal edits. No other-app installation branch remains in the user-facing setup flow.
- Missing skill install or hook audit dependency is visible and blocks affected work, not an implicit bypass.

## Local verification

- Projected real workspace has no maintainer skill tree, persona source library or packaged skill copies. Installed-package integration covers indexes, hubs, audit, task/template availability, exact-content recovery and the standalone Git audit hook with an isolated home.
- Failure probes cover path traversal/link escapes, nonempty destinations, source overlap and interrupted fresh copies. An interrupted copy leaves the destination retryable.
- Converter regressions preserve Cowork-owned setup and runtime skills, translate project-template pointers, refuse a pre-existing `.partial` directory and reject output under the source/workspace. The last two fix an older data-loss risk found during review of the already-changed converter.
- Style tooling found no repository Python/Markdown formatter configuration; no baseline reformat or tooling setup was applied. Generated packages and manifests are rebuilt artifacts, not hand-cleaned sources.

## Limits

Automated fixtures can verify copied files, scripts, memory/task contracts and failure paths. Native Cowork Save skill cards and restricted-system access still need an owner test; do not claim them exercised locally.
