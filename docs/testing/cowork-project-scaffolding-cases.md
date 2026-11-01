# Cowork project scaffolding verification

## Scope

Port starter-agent `8d248ad` to the Cowork edition without replacing Cowork instructions, environment memory, installed-skill workflow or existing owner notes. CLAUDE.md and .claude/ remain the operational paths. Owners install ready-made .skill packages with Save skill cards; source edits do not update installed copies.

## Evidence

- Baseline memory audit and 36 converter/package tests passed before changes.
- Ported hub/schema regressions failed against the old Cowork implementation: configured project folders and READMEs were missing; empty folder lists and escaping links were mishandled; unsafe schema values were accepted.
- The scoped port passes 168 personal-memory tests and 6 memory-setup tests, including CLI checks for spaces, Unicode, repeated generation and drift.
- New converter regressions were observed failing for missing project/evidence files and inclusion of the upstream internal plan. Converter file lists now handle those cases.
- A new memory-setup package/source comparison failed for the stale installed package, alongside existing personal-memory package checks. Rebuilding the ready-made packages is part of this port, not an instruction for owners to build them.
- `cowork-project-scaffolding-check.py` validates actual manifest hashes, updated package fingerprints, exact changed-skill reporting against the committed prior package index, and Python 3.10 syntax for touched scripts. Refreshing metadata is an explicit maintainer operation.

## Limits

No native Claude Cowork or Windows session has been exercised. Linux tests and Python 3.10 grammar checks do not establish native-client behavior. No owner skill was installed or changed in their Cowork account; the updated packages must still be saved there. No live system, dependency, starter-agent or example bot was changed.

## Final checks

168 personal-memory, 6 memory-setup, 39 converter/package and 9 hook tests passed. Generated indexes/hubs and the memory audit pass. All 1402 listed manifest hashes and Python 3.10 grammar checks pass after the final package build. Exactly personal-memory and memory-setup are detected as changed; their ready-made packages match the source files.

The real starter-agent checkout was converted into a disposable Claude-layout copy at `/tmp/cowork-project-conversion-h2gWGe/converted`. It completed without warnings, included projects/README.md, and excluded the root AGENTS.md/.agents layout and upstream internal plan. This is a conversion check, not a native Cowork setup run.

Fresh read-only interpretation probe `10316914c89748fb8be35d621e78e1cc` identified the project-only layout, task/procedure homes, pre-install source reading, Save skill cards, empty-state completion and upgrade preservation. It also raised broader task-migration and generic-adaptation concerns; these were not tested as actual failures and are not expanded into this scoped port. Optional client_folder defaults and owner-preserved preference notes are intentional existing contracts.

Independent reviewer `d2429acb83ac4c90abe088e572e3f281` found one actionable issue: the README manifest hash had drifted when a separate documentation commit arrived during the session. That commit was preserved; this session's README diff is only the project section. The final package build refreshes that hash, and the full hash verifier is rerun after all document edits. No other actionable finding was reported.

Repo-specific Ruff and Markdown configuration is absent; style-check skipped those surfaces. No formatter or dependency was installed. Pre-commit secret scanning, audit and all discovered skill/hook tests are run before the local commit. No native Cowork, owner-account installation or push is claimed.
