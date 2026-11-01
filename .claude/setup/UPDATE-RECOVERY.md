# Controlled updates and retained recovery

## Current boundary

Experimental helper for Claude Cowork's Linux sandbox, Python 3.10+ and standard library. The verified complete backup in `README.md`, "A newer version arrived", remains mandatory. This helper adds code-enforced scope and restartable content recovery; it is not yet the normal no-full-backup update route. File-content primitives were tested in Cowork; the shipped helper and ordinary ZIP prompt need their own acceptance.

The owner keeps the same workspace folder. Claude runs the commands; do not ask the owner to write JSON, choose commands or install dependencies. Stop editors and sync activity affecting planned files. Changes to installed Cowork skill cards remain separate.

## Run the controlled update

1. Stage the attached ZIP outside the workspace as usual and verify the full backup. Inspect without changing workspace files:
   `python3 "<Release>/.claude/cowork/update.py" inspect "<Release>" "<workspace>"`.
   This checks projected user files and baseline ownership only, not the document tree. Seed/local files and unknown edits to those paths are not replacement candidates. Unlisted workspace content is not scanned and must remain untouched. CRLF-only changes need no separate decision. An obsolete path is review-only, not a removal instruction.
2. Resolve actual conflicts and show the exact proposed file changes in plain language. Obtain approval for that scope and persistent `.workspace-backups/` recovery location. Add its Git-ignore/search exclusion as a planned edit when absent. Keep `.git`, skill sources, recovery snapshots and unrelated files untouched. Follow installed personal-memory and task/proposal recovery before their governed edits. Recovery directories stay outside recall; Git ignore is not encryption or access control.
3. Claude stages approved merged content and any generated indexes/hubs in separate scratch, then creates `operations.json` there. Never write merged/generated output directly into the workspace around the helper. Use raw-byte hashes, not normalized manifest hashes, for before/payload checks:

   ```json
   {
     "version": 1,
     "workspace": "<actual current sandbox workspace path>",
     "operations": [
       {"path": "README.md", "action": "write", "before_sha256": "<raw old sha256 or null if absent>",
        "payload_path": "<absolute staged regular file>", "after_sha256": "<raw staged sha256>"},
       {"path": "old-guide.md", "action": "remove", "before_sha256": "<raw old sha256>"}
     ]
   }
   ```

   The hashes above are placeholders, not runnable values. Every operation is a file, not a directory. A removal retains its bytes in quarantine. Owner content requires its own specific consent. Forbidden paths, case aliases, links, hardlinks, unknown fields and overlapping file/parent operations are rejected.
4. Prepare persistent recovery:
   `python3 "<Release>/.claude/cowork/update.py" prepare "<workspace>" "<operations.json>"`.
   It checks available space and current bytes, freezes old and new content, saves a standalone restore helper, verifies hashes and prints the exact operations, transaction path, plan id and current package bytes. A failed or interrupted preparation stays retained as `.preparing-*` and never grants apply permission. Prepared transactions block another update until restored/resolved. Do not manually delete evidence to clear a blocker.
5. Recheck that printed operations match the approved scope, then run:
   `python3 "<Release>/.claude/cowork/update.py" apply "<transaction>" --approved-plan "<plan id>"`.
   This flag records approval already obtained from the owner; it cannot create permission. Only frozen payloads are used. Any failed write/check stops subsequent operations. Do not blindly resume an interrupted apply; inspect status and offer approved recovery.
6. Verify applied file hashes and task/memory/project consistency. Run read-only audits; if indexes/hubs need writes, generate those in scratch and prepare a new bounded transaction. Unexpected new changes require a new scope review, recovery package and necessary approval, not edits outside the helper. Report unfinished verification rather than call the update complete.
7. Compare changed skill cards as prescribed by the setup guide against the full backup, or the helper's verified `<transaction>/baseline/` directory when its retained old package index exists. Keep the workspace package index unchanged until selected installs are confirmed. Present cards from staging and let the owner click **Save skill**; partial installs stay pending.
8. Only after checks and selected card confirmations, stage the projected manifest without `source` fields and the appropriate package index as explicit bookkeeping operations. For a successor transaction include `"predecessor": "<current applied update-directory name>"` in the operation document. The helper permits only the current applied tip and requires newest-first restore. No branching or automatic chaining of unapproved changes. Commit only session-owned changes if Git is used; Git metadata is not restored by file rollback.

## Inspect or restore after failure

Status is read-only:
`python3 "<Release>/.claude/cowork/update.py" status "<transaction>"`.

Identify later work, show recovery scope and obtain current restore approval. The helper retains displaced update bytes; conflicting later edits or unexpected files in update-created folders stop recovery before changes. Never override a conflict by deleting the newer content.

Restore from persistent files, even in a later Cowork session with no old Release staging:
`python3 "<transaction>/restore.py" rollback "<transaction>" --approved-plan "<plan id>"`.

Rediscover the transaction under the current mount, not an old `/sessions/` path. Restore newest dependent transaction first. Restore can restart after its own interruption at the tested boundaries; it checks original bytes and absence and moves update-created content into quarantine rather than deleting it. A corrupt/truncated journal or ambiguous temporary file is a safe stop requiring inspection, not permission to guess. The full backup remains the fallback for manual recovery of ambiguous states. Retain all packages and quarantine; no automatic pruning.

## Honest limits

- Content and presence/absence only. Cowork ignored chmod in the mounted-folder probe. No file-permission, ACL, alternate-stream, Windows attribute or timestamp guarantee.
- Kernel locking excludes other helper processes in the sandbox, not Windows apps or sync tools. Outside concurrent writers are unsupported.
- Successful file/directory sync calls do not prove Windows-host power-loss durability. Partial temp bytes after an abrupt failure can require manual inspection; do not claim recovery at every possible crash point.
- Internal recovery does not protect against losing the workspace folder or disk. Full backup remains required by current policy and useful for broader protection after any future change.
- Workspace rollback does not undo Cowork Save skill actions or rewind Git commits. Explain their separate status.

## Acceptance before changing the default

Run the actual shipped code inside a unique synthetic child of the disposable Cowork copy: normal apply/restore, interrupted apply and restore, later-edit refusal, corrupt-state refusal, moved staging and exact original/unrelated bytes. Then test an ordinary attached-ZIP option-3 flow, including pending-card/final-manifest handling. No passing local suite or earlier throwaway prototype substitutes for those checks. Until both pass, retain the experimental label and complete-backup requirement.
