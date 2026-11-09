# Shipped Cowork updater: native evidence, 2026-11-01

## Result

The actual helper at commit `4900c9b` completed a synthetic mounted-folder CLI update and exact-content restore. Native suite acceptance is incomplete: its snapshot helper hid all fixture contents under a `.workspace-backups` ancestor, and staging omitted `.gitignore`. No ordinary attached-ZIP prompt or installed-skill acceptance is established. Full backup remains required.

## Evidence

Windows evidence root: `<test workspace>\.workspace-backups\20261101T233638Z-shipped-updater-2ec6a7`.

- `report.json` records Python 3.10.12, seven unchanged-suite chunks, five location-corrected chunks and two CLI smoke attempts. All eight staged source hashes were independently rechecked against `source-sha256.json`; no mismatch.
- Unchanged suite: 35 collected, 31 passed, two errors, two skipped. Snapshot-dependent assertions are unreliable in that location. Errors: empty snapshot and omitted `.gitignore` staging input. Real symlink/hardlink cases were skipped by scope, not passed.
- Runner-only relative-snapshot adaptation: 35 collected, 32 passed, one omitted-file error, two skipped. Not a clean unchanged-suite pass. Twelve collected cases repeat inherited base tests; there are 23 unique methods.
- Passing CLI attempt: `results/cli-smoke-smoke-6fa30f.json`, 15 checks independently counted, none false; 12 command receipts, with only the deliberately refused older-first restore returning nonzero. Verified synthetic full backup, exact update bytes, pending bookkeeping unchanged, successor-first recovery, retained helper after staging moved and exact original bytes/absence restored. First fixture attempt lacked required release inputs and is retained as unsuccessful setup.
- Fresh first recovery package: 27,055 bytes including retained helper, plan, marker, instructions, baseline and blobs; independently matched to CLI count. CLI fixture duration: 31.17 seconds. Neither predicts real workspace performance.

## Local repair and remaining check

Snapshot exclusion now examines paths relative to the fixture workspace. A dedicated regression first failed with an empty snapshot instead of owner bytes, then passed after the one-line fix. Release suite: 86 passed; hook suite: 11 passed. Reviewer found no blockers against `CODING_STANDARDS.md`. No engine behavior changed. Python formatting skipped: no repository Ruff configuration; no tooling installed.

A native rerun with repaired committed tests, `.gitignore` staged, and no snapshot runtime adaptation remains required. Preserve original evidence. Two real-link cases remain excluded by scope. No Save skill clicks, real workspace updates, pushes, metadata or power-loss guarantees were tested. Observer reached its limit while Cowork appeared busy; saved reports, not observer exit, support these findings.
