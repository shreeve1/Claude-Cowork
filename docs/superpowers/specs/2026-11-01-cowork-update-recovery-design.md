# Reliable Cowork updates: design

## Intent and authority

James approved building the reliable process discussed on 2026-11-01: close prototype safety gaps, ship a controlled update/recovery helper, integrate guided instructions, and run acceptance in disposable `itastack - Copy`. No push or installed-skill change is authorized. The details below are builder recommendations for review before product code changes.

Keep the existing workspace folder. Claude handles technical work; the owner approves actual changes and meaningful conflicts. Preserve what the update can change rather than guessing which content is personal.

## Flow

Attached ZIP -> read-only inspect -> resolve conflicts -> approve exact changes -> prepare/verify recovery -> controlled apply -> verify -> separate selected skill-card confirmation -> final bookkeeping.

Interruption -> inspect persisted state -> approved recovery -> refuse conflicting later edits -> safely restart recovery. Retain original and displaced bytes.

## Constraints

- Python 3.10+, standard library. Preserve filtered fresh creation and `workspace.py plan`. Tools run from extracted Release; no daily-work dependency on staging.
- Targeted recovery stays experimental until the acceptance gate passes; only then replace mandatory full-copy guidance. Full backup remains available for whole-folder loss or metadata requirements.
- Manifest membership is not replacement approval. Preserve owner notes, rules, task identity/history/proposals, schema choices, custom skills, documents, Git/remotes and unrelated files unless specifically included and approved.
- Cowork Save skill and Git commits are outside file rollback. No automatic cleanup, recursive deletion, Git reset, push, new dependencies or discarding owner bytes. Approved removals move into retained quarantine.

## Proposed implementation

Add `.claude/cowork/update.py` (inspection/CLI) and `.claude/cowork/update_recovery.py` (bounded transactions). Implement from tests rather than promote the throwaway prototype wholesale.

Unique transactions live in `<workspace>/.workspace-backups/`. Verify persistent storage, safe paths, access and free space; restrict supported permissions. Ignore/search exclusions are not encryption or guaranteed Windows access control. Existing ignore changes are planned edits. Never use session-only recovery storage.

Retain frozen plan/payload, exact old bytes, supported modes, absent files/parents, integrity records, journal, quarantine and restore instructions. Keep verified stdlib restore code in the transaction so recovery needs no old session staging. Hashes detect corruption, not malicious replacement of the entire package.

Use bounded linked transactions: workspace edits first, then index/final manifest after audits and confirmed selected skill installs. Restore newest first; refuse earlier recovery while a newer dependent transaction remains applied/unresolved. Incomplete card installs or finalization stay pending.

Interrupted apply is inspected and rolled back with approval, not blindly resumed. Rollback must survive interruption itself, including after moving current bytes away but before restoring old bytes.

## Exact scope

Read-only inspection compares projected user files with installed baseline and current state: unchanged/CRLF-only, shared candidates, seed/local, owner-edited/unknown, missing and obsolete candidates. Never scan unrelated document trees or remove legacy sources automatically.

Each approved operation names one canonical relative file, write or retained removal, expected raw before hash/absence, payload hash and supported mode. Stage merged and generated index/hub files before freezing the plan; no update writes around the helper. Package index and manifest writes are explicit operations too.

Preparation freezes operations and verifies original/payload copies. Apply requires the matching plan id and revalidates source state. A CLI flag asserts already-obtained consent; it cannot grant authority. Extending scope needs a new verified transaction and necessary consent. Reject unknown fields/actions and identity mismatch.

Keep installed personal-memory and task/proposal recovery checks before their governed edits. Auxiliary snapshots remain retained evidence, not a rollback substitute. Stage generated outputs in scratch and plan their writes. Git commits are a separate optional finish; rollback does not rewind Git internals.

## Safety

- Reject absolute/drive/UNC paths, traversal, backslashes, empty components, Windows reserved names, trailing dots/spaces, alternate streams, case aliases/collisions and file-parent overlap. Forbid `.git`, transaction storage and legacy skill-source trees as targets.
- Check root, every touched ancestor, payload and recovery paths. Reject symlinks, detectable reparse/junctions, nonregular and multiply linked files, and existing filename-case aliases even on a case-sensitive sandbox. Disclose unsupported checks.
- Enforce one helper writer with persistent state; unresolved transactions need explicit inspection/recovery. External apps must stop editing touched paths; no claim of race-proof isolation.
- Preflight recovery/payload/temp/quarantine space; also stop safely on actual ENOSPC, permission, journal, write, replace or fsync errors. No later operation proceeds after failure.
- Durable intent precedes mutation. Verify temporary bytes and use same-filesystem atomic replacement where supported. Stop on required durability failure. Directory-sync limits do not constitute power-loss protection.
- Recovery preflights all conflicts and retains displaced bytes. Journal its own intermediate operations and temp paths. Later edits, unexpected new-folder content or unrecognized temp files block destructive recovery. Matching bytes alone never proves journaled ownership.
- Recognize rollback's own displacement gap and restored-but-unrecorded state. Move only proven-created, now-empty folders into quarantine; preserve pre-existing empty folders. Verify original bytes, supported modes and absence after recovery.

## Reviewed implementation rules

The builder check raised five questions. Resolve them as follows; these are builder choices, not new owner requirements.

**Crash evidence.** Use ordered integrity-checked journal records with transaction id, sequence, phase, operation, expected hashes/modes and deterministic temp/quarantine destinations. Intent is flushed before mutation; completion is flushed afterward. For restore of an existing file, prepare and verify its original-byte temp before journaling displacement. The restart table is:

| Target | Recorded rollback destination/temp | Action |
| --- | --- | --- |
| Planned update bytes | No displacement yet | Verify temp, journal displacement intent, move update bytes to exact quarantine destination |
| Absent after recorded displacement intent | Matching displaced update bytes and verified original temp | Restore original temp atomically |
| Original bytes/mode | Valid matching restore intent, possibly temp already consumed | Verify and record completion; retain quarantine |
| Newly created target absent | Journaled update mutation plus matching quarantined update bytes | Record original absence restored |
| Anything else or duplicate/unexpected artifact | Any | Refuse with exact path; preserve everything |

Apply restart is recovery-only. Its intents similarly record exact temp/removal destinations; untouched operations remain untouched. A truncated final journal record is a stop requiring inspection, not permission to ignore a possibly completed action. Do not automatically truncate or rewrite evidence. Tests must distinguish a recoverable committed intent from damaged evidence; refusal preserves all bytes.

**Live locks.** Cowork runs this tool inside Linux. Use a stable lock file in recovery storage with nonblocking kernel-held `fcntl.flock` around prepare/apply/rollback. Process death releases the kernel lock, so a leftover file is not treated as a live writer and is never deleted to guess liveness. Persistent lifecycle state still blocks new updates until recovery/resolution. If flock is unavailable or demonstrated ineffective on the mounted storage, stop this route; no PID-age heuristic or silent weaker fallback. Direct native Windows execution is not an initial supported runtime, though Windows-safe target names and detectable reparse validation remain required.

**Dependency rules.** Every transaction after the first declares the current applied tip as predecessor. Create finalization only after workspace verification and selected-card confirmations; before then the workspace transaction reports applied/pending finalization. A prepared, interrupted or applied child blocks parent restore until that child is restored/resolved. A fully applied tip permits a newly approved successor; unresolved/failed/rolling-back state does not. Restored children no longer block their parent. Branching and cycles are rejected. Read dependencies from verified direct-child transaction records under the same storage root, never caller-supplied arbitrary paths. An incomplete child record blocks rather than being ignored.

**Ownership proof.** A mutation needs a verified plan entry plus durable intent for the exact target/artifact and the expected byte/mode state; folder ownership also needs a durable creation intent and absent-before evidence. Retained artifact paths are transaction-specific, created exclusively and never overwritten. Where stable, record filesystem identity/stat observations as extra conflict evidence, not portable proof across sessions. Empty pre-existing folders and unjournaled matching files remain owner content. If journal/disk state is ambiguous, stop rather than infer permission.

**Later work boundary.** Changed touched-file bytes/modes, replaced parents, unexpected new-folder contents and modified/unknown temporary artifacts block recovery; unrelated edits outside the operation/created-parent scope do not. An edit changed back to identical bytes/mode is not reliably detectable, and concurrent outside writers are unsupported. State those limits honestly; the helper protects against observable conflicting state, not every edit history. Preserve original bytes for manual recovery when evidence is ambiguous.

## Integration

Keep `.claude/setup/README.md` authoritative; update directly conflicting manifest/adaptation/top-level README and workspace seed references. After acceptance: “I'll save recovery copies of the files this update will change. Your other files will stay untouched. No extra folder selection is needed.” Show visible recovery location and actual changes before approval; explain whole-folder/disk-loss limits. Unsuitable internal storage stops this route and prompts a concrete persistent full-backup recommendation.

Retain verified old package index under its original relative path in recovery evidence for `cowork_skills.py changed`. Keep the workspace's old index until selected card installs are confirmed; partial installs remain pending. Recovery explains separately which saved skill cards need attention.

## Acceptance

1. Unit/subprocess tests: normal apply/recovery, every meaningful apply and rollback interruption boundary, exact bytes/modes/absence/empty folders, preserved quarantine and unrelated sentinels.
2. Negative tests: Windows case aliases, unsafe links, corrupt/truncated plans/journals/packages, drift, unexpected payloads, disk/write/journal errors, missing helpers, later edits and competing writers. Fault injection stays in tests, not hidden production crash flags.
3. Fresh-process restore with staging unavailable; linked finalization and reverse recovery; preserve pending-card state.
4. Existing projection/conversion/package/memory/task tests and manifest checks pass; reviewer checks risk diff against CODING_STANDARDS.md. New tools/tests stay maintainer-only.
5. Native Cowork test in unique synthetic child inside `itastack - Copy`, revised ZIP and ordinary option-3 prompt: actual helper commands, interrupted apply/rollback recovery and later-edit refusal. Preserve existing files and installed skills; no Save skill clicks. Save receipts, actual package bytes and timings. Never call a synthetic subset an update of the entire real copy.
6. Switch default only after acceptance. If desktop access/native approvals block it, retain experimental gate and report the exact gap. Local tests alone are not production readiness.
