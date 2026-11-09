# Cowork updater feasibility: 2026-11-01

## Result

The small file-content update/recovery core is feasible in the tested Claude Cowork mounted folder. A test-only prototype passed 12 tests and 11 explicit subtests. This is not the production updater and does not prove an ordinary attached-ZIP update prompt works end to end.

## Where this ran

Actual Windows Claude Cowork, existing disposable test conversation, Python 3.10.12 inside its Linux sandbox. Probe and fixture files were on the mounted `test-workspace copy` folder, not just private Linux scratch. All cases used fresh synthetic data in a unique run. No real release update or skill installation was performed.

Evidence root:
`<test workspace>\.workspace-backups\20261101T224159Z-cowork-feasibility-3692fa`

Maintainer-readable root:
`<test workspace>/.workspace-backups/20261101T224159Z-cowork-feasibility-3692fa/`

The desktop observer timed out, but Cowork had finished. Outcome evidence was read from saved files, not inferred from the observer's exit.

## What passed

- Mounted-folder probes: exclusive create, file/hash readback, file/directory fsync calls returning successfully, overwrite by `os.replace`, same-mount file/folder moves into quarantine, stat/free-space lookup and existing case-alias detection by listing siblings.
- `flock` blocked a second sandbox process while held. After killing the holder, another process acquired it. A restore also refused while another process held its case lock.
- Normal update/restore restored original raw bytes and original absence; retained removed/updated contents in quarantine; preserved unrelated files and an empty folder.
- Fresh-process recovery after update interruption and after restore interruption: after displacement but before old bytes were restored; after creating a restore temp; after restoring bytes; before recording overall completion; after moving the new file or its created folder into quarantine.
- Later edits and new owner content in an update-created folder caused refusal before restore mutations. Corrupt saved bytes, truncated plan and corrupt middle journal records were refused in the tested cases.
- Injected failure immediately before replacement stopped later operations, then recovery succeeded. This was a test-injected I/O error, not a real full-disk or permission-exhaustion test.
- Restore succeeded with the synthetic staging folder moved away.

Saved suite: 12 top-level tests, zero failures/errors, 23.95 seconds. Counted 11 passing explicit subtest outcome rows. The runner's separate `subtest_rows_pass` field incorrectly says 0 because its label parser checks parentheses while labels use square brackets; the explicit outcomes support 11. Saved 60 helper command receipts include 11 injected `os._exit(137)` exits, followed by fresh helper processes. These are process interruptions, not power-loss tests. Two additional tamper/missing-file controls refused with workspace unchanged.

Main independently inspected the tests/helper/receipts and directly checked restored case files: original instructions/bookkeeping/removal-target bytes, absent new folder and intact unrelated note sentinel. No test was rerun outside Cowork to establish its mounted-filesystem capabilities.

## Limits that affect the build

- `chmod` returned without error but did not change mode bits. Do not require or promise file-permission recovery on this mount. Windows access-control lists, streams, attributes, timestamps and reparse points were not validated.
- Locking is proved only between Cowork sandbox processes, not against Windows editors, Explorer or sync tools. Stop outside editing during updates/recovery. Concurrent owner edits during a running restore were not detected by this prototype.
- Successful fsync calls do not prove Windows-host power-loss durability. Partial writes, kernel crashes and power loss were not tested.
- The fixture has six original files and four planned paths. No full workspace update, production hardening, frozen-payload integration, final-manifest/card handoff or ordinary end-user prompt acceptance has been proved.
- The reported 654–1,160-byte per-case recovery package counts the prototype's `rec/` contents only, not its helper, journals, payloads and quarantine. It is not a finished production package-size estimate.
- The prototype uses same-mount quarantine moves, not deletion. Its code is test-only; passing these tests is not approval to copy it unchanged into production.

## Next implementation boundary

Use these proven basic operations for the smallest controlled helper, retaining existing projection and approval safeguards. Test additional behavior only as implementation needs it. Keep shipped full-backup policy until a complete replacement passes acceptance; saved skill cards remain separate from workspace rollback.

## Source files

Within the evidence root: `report.json`, `probe.json`, `probe.py`, `fx.py`, `test_fx.py`, `run_fx_tests.py`, `results/run1-outcomes.json`, `results/run1-commands.json`, `results/negative-controls.json`, and `cases/run1/`.
