# Reliable Cowork updater: implementation plan

**Goal:** Approved same-folder changes with verified targeted recovery that survives interruption during update or restore.
**Architecture:** Read-only comparison -> exact approved plan -> bounded persistent transaction -> separate selected skill confirmation -> linked bookkeeping transaction.
**Stack:** Python 3.10+, standard library, unittest, existing projection/package tools, native Cowork acceptance.
**Spec:** `docs/superpowers/specs/2026-11-01-cowork-update-recovery-design.md`.
**Status:** Owner approved the minimal Cowork-proven build. Baseline: 50 release tests pass. Implement inline with a final independent risk review.

## Implementation rulings after Cowork feasibility

- Use content bytes and presence/absence only: the mount ignores chmod. Remove mode preservation from this build; report Windows metadata limits explicitly.
- Keep one exact operation document and one small stdlib transaction engine. Link only successive approved transactions for newest-first restore, not a general workflow framework.
- Use the existing checkout for this tightly scoped local build, with exact-path commits and a clean baseline; no external branch/worktree lifecycle.
- No hidden production crash flags. Tests terminate subprocesses through an injected Python callback. Native Cowork tests invoke the same shipped code.
- Frozen restore code and bytes persist inside the attached folder; derive the workspace from that location so session mount-prefix changes do not break recovery.

## Global constraints

No push, installed-skill change, owner reset, recursive deletion or source-tree copy. Preserve memory/task recovery protocols. Enumerate every update write and generated bookkeeping change. Recovery is persistent and retained under `.workspace-backups/`, excluded from recall/Git. Keep the new route experimental until native acceptance passes.

## Files and interfaces

Create `.claude/cowork/update.py` (comparison/CLI), `.claude/cowork/update_recovery.py` (transactions), `.claude/skills/convert-release/tests/test_cowork_update.py` and `test_cowork_update_failures.py` in the same test directory. Update directly conflicting guide/seed files, `.gitignore`, `CHANGELOG.md`, `MANIFEST.json` and necessary generated artifacts only. Acceptance summary: `docs/testing/`; generated receipts: ignored `artifacts/cowork-update/`.

CLI:

```
python3 <Release>/.claude/cowork/update.py inspect <Release> <workspace>
python3 <Release>/.claude/cowork/update.py prepare <workspace> <operations.json>
python3 <Release>/.claude/cowork/update.py apply <transaction> --approved-plan <id>
python3 <Release>/.claude/cowork/update.py status <transaction>
python3 <transaction>/restore.py rollback --approved-plan <id>
```

Inspect/status never write. Prepare returns id, exact operations, byte counts and persistent location after verification. Matching ids assert consent already obtained, never grant consent. JSON errors provide stable code, affected path and next safe action without private contents. Status distinguishes prepared, failed, applied, rolling-back and restored.

Operation document v1: workspace identity, optional predecessor id, explicit entries `{path, action, before_sha256|null, payload_path|null, after_sha256|null}`. Payloads are separate-staging regular files frozen by preparation. Write requires payload/hash; retained removal requires existing before hash. Reject unknown keys/actions and identity mismatch.

## Task 1: Inspection and scope validation

**Produces:** `inspect_release(source: Path, workspace: Path) -> dict`, `validate_operations(workspace: Path, document: dict) -> dict` in `update.py`; filesystem checks in `update_recovery.py` as appropriate.

- [ ] Write failing tests: CRLF-only equality, shared candidates, preserved seed/local, owner-edited/unknown ownership, missing/obsolete entries and unchanged inspection tree.
- [ ] Add path tests: existing case aliases at each ancestor, reserved names, traversal, symlinks/reparse simulation, hardlinks, excluded control namespaces, Unicode/spaces and parent overlap.
- [ ] Run `python3 -m unittest discover -s .claude/skills/convert-release/tests -p test_cowork_update.py -v`; confirm expected missing behavior fails.
- [ ] Implement comparison via `workspace.project`, strict validation and CLI inspect. Check relevant paths only; manifest membership is never permission to overwrite.
- [ ] Rerun focused tests and `test_cowork_workspace.py`; review and commit exact owned paths.

## Task 2: Preparation and controlled apply

**Consumes:** validated operations. **Produces:** `prepare_transaction(workspace: Path, document: dict) -> Path`, `apply_transaction(transaction: Path, approved_plan: str) -> dict`, `transaction_status(transaction: Path) -> dict` in `update_recovery.py`; CLI prepare/apply/status.

- [ ] Add failing tests: exact bytes/absence, absent files/parents, sealed-copy verification, drift, unexpected payloads, insufficient space and competing writers.
- [ ] Add copy/write/fsync/replace/journal failure tests; assert no later operation runs, preparation failures never alter target bytes and mutation failures retain recoverable state.
- [ ] Implement unique persistent transactions, supported private permissions, frozen payload/originals, integrity records and copied stdlib restore launcher/code. Retain old package index at its original relative path for existing comparison compatibility.
- [ ] Implement durable intent, verified temp writes, retained removal and explicit lifecycle/intermediate states. Reject unresolved transactions and mismatched approval ids.
- [ ] Probe subprocess CLI in Unicode/spaced paths, rerun Task 1 checks; reviewer checks data-loss boundary against CODING_STANDARDS.md, then commit.

## Task 3: Restartable recovery

**Consumes:** retained transaction/journal. **Produces:** `rollback_transaction(transaction: Path, approved_plan: str) -> dict`, runnable without original staging.

- [ ] Write failing subprocess tests interrupting apply before/after intent, temp write, replacement, retained removal and completion. Assert exact fresh-process recovery and unrelated sentinels.
- [ ] Write rollback interruption tests: displacement/before restoration, restored/before journal completion, temp creation, created-folder quarantine. Repeated recovery safely completes or refuses genuine conflict.
- [ ] Test later edits, unexpected new-folder contents, changed temps, corrupt/truncated journals/packages and unknown states. Corrupt middle records must not be mistaken for torn tails. Conflict preflight leaves workspace unchanged.
- [ ] Implement the spec’s reviewed crash-state table, kernel-held `flock` and immutable predecessor rules, with explicit rollback journal/ownership/intermediate states and test-only filesystem fault injection. Retain displaced data; never recursively delete. Matching content alone does not authorize removal.
- [ ] Test linked finalization and reverse recovery; reject unsafe ids/moved roots and preserve pending-card state. Test restore with staging unavailable.
- [ ] Run both new suites, obtain fresh risk review and commit exact owned paths.

## Task 4: Guided integration and acceptance

**Consumes:** helper, old-index evidence and `cowork_skills.py changed`. **Produces:** experimental instructions/evidence, then default switch only when accepted.

- [ ] Add failing documentation/packaging checks for persistent restore, old-index comparison, memory/task snapshots, explicit bookkeeping and excluded maintainer files.
- [ ] Update authoritative setup: inspect -> resolve/approve -> installed recovery checks -> stage merges/generated outputs -> freeze plan -> prepare/verify -> apply -> read-only verification -> separate card confirmation -> linked finalization. New scope needs a verified approved transaction, not direct edits.
- [ ] Document recovery/conflicts, optional full backup, metadata limits, one-writer boundary, Git exclusion and partial installs. Add recovery Git/recall exclusions as planned existing-workspace changes.
- [ ] Register new maintainer files/refresh release hashes; regenerate packages only if sources change. Run release tests, hook tests, memory audit and manifest checks. Inspect failures instead of repeating passing checks unchanged.
- [ ] Commit verified code before desktop work. Drive Cowork in unique synthetic child inside `test-workspace copy`, revised ZIP and ordinary option-3 prompt. Record commands, actual package bytes/timings, interrupted apply/rollback and later-edit refusal. No Save skill clicks.
- [ ] Switch normal guidance only after acceptance; otherwise retain experimental gate and report blocker. Run cleanup, fresh standards/risk review, final focused tests, memory capture/audit and exact-path commits. No push.

## Verified build ledger

- Baseline: 50 release tests passed before edits. Initial 12 core contract tests failed for the missing engine; interruption tests failed before implementation.
- Core/CLI/integration: 35 updater tests and 85 total release tests passed. Hook suite: 11 passed. Memory audit passed. Active Python diagnostics have no reported errors.
- Risk review found partial-restore-write and interrupted-preparation gaps. Added regression tests (failed first), then staged original temps before displacement and published prepared directories only after sealing. All updater tests passed afterward.
- Final risk review found no important unsafe-restore defect. Its suggestion to enumerate every unknown document conflicts with the scoped no-tree-scan goal; retained scoped inspection and explicitly documented unlisted-content preservation instead.
- Style tooling skipped Python/Markdown because no repo formatter/linter config is declared. No tool installation or baseline formatting was added.
- Next gate: native Cowork tests of these actual shipped sources, not the earlier throwaway prototype. Ordinary ZIP-flow acceptance and default-policy switch remain pending.

## Review focus

Tests explicitly cover rollback displacement gaps, Windows/reparse aliases, journal failure after mutation, later owner content matching update bytes without journaled ownership, and interruption between workspace changes/card confirmation/final manifest-index writes.

## Recommended execution

Native execution in this session, followed by fresh risk review. The transaction stages share tight state-machine contracts; one implementer avoids divergent recovery assumptions. A fresh implementer/reviewer per task is the alternative if James prefers it.
