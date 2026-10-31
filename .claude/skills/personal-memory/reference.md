# Personal Memory Reference

Rare operations for the `personal-memory` skill: recovering missing scaffold, linting memory health, Client Memory, the weekly sweep and procedures. `SKILL.md` covers everyday capture and reads; open this file only for one of these. `<skills>` is defined in `SKILL.md`.

## Task and document formats

Saved workspace task operations are in [tasks.md](tasks.md); read it on create, lookup, continue, review, complete or archive requests. Copyable records/indexes are in [task-templates.md](task-templates.md). Pending proposal and general research formats are in [supporting-templates.md](supporting-templates.md), reached when producing those records. They ship beside this reference, including in global or copied installs.

## Setup Workflow

For setup and migration, use the `memory-setup` skill.
Copy missing scaffold from `<skills>/personal-memory/scaffold/`.

## Recovery Workflow

Scaffold or personal files may be missing in a fresh copy of a
project. Before writing any promoted memory in a run, ensure the scaffold
exists first, then recover the personal files:

- If `memory/README.md` or `memory/TEMPLATES.md` is missing, recreate it — it is
  scaffold, not personal state. Restore `README.md` as the memory
  contract and `TEMPLATES.md` as the canonical templates, copying it from
  `<skills>/personal-memory/scaffold/`.
- If `memory/index.md` is missing, recreate it from the `TEMPLATES.md` index template before writing promoted memory.
- `memory/log.md` is retired. Never recreate it.
- If `TEMPLATES.md` is itself unavailable, do not block: fall back to the
  templates embedded in this skill and the format docs, and recreate
  `TEMPLATES.md` from them.
- Missing personal files are normal, not an error.

## Recovery before editing

Before editing any existing hand-written memory (replacing, deleting or adding to it, including adding a row), preserve its exact previous bytes, including uncommitted notes and memory/index.md, rules.md and glossary.md. New files need no snapshot; only generated topic indexes and hubs are rebuildable exceptions. Use the same protocol with or without Git.

1. Read the source, check authority and confirm this task owns the intended edit.
2. Run `python3 <skills>/personal-memory/recovery.py --root <workspace> snapshot memory/<path>.md`. Quote paths containing spaces for the shell. Success returns a verified unique copy under `<workspace>/.memory-recovery/<id>/memory/...`; failure means stop before editing. If the source changed after a verified copy, the helper retains that copy and reports its path; it still grants no permission to edit. Absolute, drive, backslash, parent-traversal and symlink paths are rejected.
3. Re-read the source immediately before editing and compare it with the snapshot. A changed source means stop, re-read and re-ground; preserve the intervening change. Only then replace or delete the intended content.

Without Python, use file tools to copy into a unique `.memory-recovery/` location, re-read both and verify exact previous content before editing. Text-only tools cannot guarantee unknown encodings or binary bytes; if exact preservation cannot be verified, stop and ask for suitable tools. Disclose that automated audit and byte checks were unavailable; manually check links, rules, templates and size limits.

This is a single-writer protocol, not a race-proof transaction or lock. The helper only makes backups; it never restores, replaces or deletes the source. Keep snapshots outside routine recall, ignored with `/.memory-recovery/` at the workspace root; never automatically prune. They may contain sensitive summaries: ignore rules are not encryption or access control, and secrets remain forbidden.

To restore, show the selected snapshot and target, obtain owner approval, preserve the current target first with this protocol, verify the selected content, then restore and check indexes/hubs and audit (or disclosed manual equivalents). Retain the old workspace and recovery during upgrades; copy recovery separately only with owner approval, never as part of a release copy.

## Lint Workflow

Use when asked to review memory health or before broad cleanup.

Run the deterministic index audit first:

`python3 <skills>/personal-memory/gate.py --memory memory audit`

Without Python, use the hand checks in `SKILL.md` Capture Workflow step 6, then review the items below. Say that the audit was not run.

It reports promoted files missing from `memory/index.md`, index entries pointing to files that no longer exist, topic-folder problems (a promoted file directly in `workflows/`/`decisions/`, a topic folder not in `memory/schema.json`, a sub-index missing a file or drifted from `indexes.py`), and Client Memory problems (missing frontmatter keys, unknown subject, subject/client not matching the folders, note not on its hub, hub out of date, hub without an `index.md` row), and exits non-zero when anything needs fixing. It also prints `crowded` warnings (a memory folder holding more than 15 `.md` files directly) but does not fail on them. Fix hub problems by running `hubs.py`; fix sub-index drift by running `indexes.py`. `memory/candidates/` is not audited. For `gate.py audit` to recognize an index entry, the row must carry the file path either backticked (`` `memory/decisions/<topic>/decision-x.md` ``) or as a markdown link (`[title](memory/decisions/<topic>/decision-x.md)`).

Then also check for:

- Index rows pointing to missing files.
- Promoted files missing from `memory/index.md`.
- Empty promoted topic files.
- Conflicting active promoted rules.
- Cross-links pointing to memory files that do not exist (report only — broken links are tolerated, not auto-removed).

Report findings before making broad changes. Safe deterministic fixes include removing stale rows and adding missing index rows for existing files.

Note on `gate.py`: `audit` checks `memory/index.md` against the promoted files and Client Memory on disk, checks `memory/rules.md`, and prints lean-memory warnings (size, summary length, history lines, superseded files). `stale` lists notes not updated or verified in 90 days. It checks structure only; it does not check whether a memory item is true (see the grounding rule in Capture Workflow).

## Client Memory

Lasting client facts live at `memory/<client_folder>/<subject>/<short>/<slug>.md`, one fact per note, template in `memory/TEMPLATES.md`. `<client_folder>` is `clients` unless `memory/schema.json` sets `client_folder` to the owner's own word (one lowercase word, for example `students`); every script and path below follows it. The word "client" in this skill means whatever the owner tracks. `<short>` is the Client Short Name from `memory/glossary.md` (add the client there first if missing). Required frontmatter: `type: client-memory`, `client`, `subject`, `title`, `verified` (YYYY-MM-DD last confirmed), `source` (ticket `"#70358"`, `"the owner said"`, or `"meeting <session8>"`).

Subjects come from the `client_subjects` list in `memory/schema.json` — the source of truth. An agent adds a subject only with the owner's approval, and `gate.py audit` fails any note whose subject is not in the schema. A subject is a kind of lasting fact the owner needs about whatever they track: `contacts` — who to deal with and how; `history` — what happened and was agreed; `preferences` — what the thing likes or needs; `temperature` — dated, sourced observations of what pleases or frustrates it (never personality guesses). Add a subject that fits what the owner tracks, for example the system that holds their records, with the owner's OK.

A fact spanning subjects is filed where a task would look first and linked (by `memory/...` path) from a short note in the other subject.

Hubs: `python3 <skills>/personal-memory/hubs.py` regenerates `memory/<client_folder>/_hubs/<short>.md` for every client found under any subject (notes by subject with verified date, plus that client's `<client_folder>/<short>/tickets/`, `projects/` and `procedures/` files). Without Python, write the hub by hand with the same note paths, subjects and verified dates, and any existing client document paths. Otherwise never edit generated hubs by hand. `hubs.py --check` exits 1 if a hub is out of date. The session writes Client Memory and runs `hubs.py`; when subagents are used, they return facts. `hubs.py` lists every note on disk, including another live session's uncommitted notes, even for the same client. In a git repo, stage only the hub lines for notes this session wrote or deleted: start from `git show HEAD:<hub>`, apply just your lines, then `git hash-object -w` and `git update-index --cacheinfo` (as `startday` step 8 does, where used). Never `git add` a whole hub.

## Weekly Sweep

Only where a scheduled sweep is set up (`WEEKLY-SWEEP.md` in a starter workspace) or the owner asks. The automated sweep needs git and Python; without either, use the Lint Workflow above and report proposed deletions instead. `sweep.py` deletes a file only when its bytes equal the committed copy, so every deletion can be undone from git.

0. `git status --short`. Another session may be mid-edit: never edit, compact, trim, merge or delete a file listed there, staged or not; name it in the final report instead. Never run `git restore`, `checkout`, `reset`, `stash` or `clean`: they discard other sessions' work. To undo your own edit, write the old text back by hand. `sweep.py` checks this itself for the files it deletes.

1. `python3 <skills>/personal-memory/sweep.py --apply`. It deletes `.sessions/` and `artifacts/` files older than 90 days, except `artifacts/startday/` (where used) and any file a note, skill or context file names. `reports/`, `memory/` and `clients/` are never aged out. Keep its output for the commit body.
2. Run `gate.py audit`, `stale`, `crowded` and `links`.
3. Apply Memory authority before maintenance: automatic content changes are limited to resolved ordinary facts. Changing, merging away or deleting standing rules, preferences, decisions or procedures needs explicit owner direction or approval, regardless of stale/superseded status. Report proposed authority changes and unresolved conflicts without editing them. Before permitted hand-written replacement, deletion, merge or trim, apply Recovery before editing. `gate.py compact` snapshots each changed root file and rechecks it before writing, including with a custom --memory directory. Generated topic indexes and hubs are exempt, not memory/index.md, rules.md or glossary.md. Within those limits, act on what they show:
   - `status: superseded`, or a note whose only content is history: delete it and its index row.
   - Stale (over 90 days): re-ground it against current files or tool output. Still true: set `updated`. False: delete it. Needs a live system you cannot reach: leave it and name it in the report. Never delete a note for age alone.
   - Two notes on the same subject: merge into one, delete the other, repoint links (`gate.py backlinks <path>` lists them).
   - Over size, or a glossary row longer than one line: trim it and move the detail into a Client Memory source note (`memory/clients/<subject>/<short>/<slug>.md`), never into a hub, which `hubs.py` regenerates. Run `gate.py compact` only when `rules.md`, `glossary.md` and `index.md` are all clean in `git status`; it rewrites every padded one of them. Otherwise leave the padding and say so.
   - Crowded folder: consolidate per the 15-file rule.
4. Run `indexes.py --check` and `hubs.py --check`. If neither would change a file, skip to 5. Otherwise run `git status --short`: when every index or hub they would rewrite or remove is clean, run `indexes.py` and `hubs.py`; when one is dirty, leave it and name it in the report. Then `gate.py audit`; if it still fails only because of a file you were told to leave, report that and stop.
5. Commit only the paths this run changed or deleted, never other sessions' files: `memory: weekly sweep <date>`, with the swept and deleted paths in the body.
6. Reply with one line: files swept, notes deleted, merged, trimmed, left for the owner.

## Procedures

Stored procedure approval does not authorize the current action. Obtain current-conversation permission under workspace safety rules. Stop at approval checks, failed steps or changed conditions and propose changes to the owner; never silently revise the recipe.

A procedure is a verified set of steps the agent follows whenever its trigger comes up: a `type: procedure` file in `memory/workflows/<topic>/<slug>.md`, shaped by "Procedure File" in `memory/TEMPLATES.md`. A runbook a person follows belongs in the project's `docs/` instead.

**Readiness before execution:** `python3 <skills>/personal-memory/gate.py --memory memory procedures memory/workflows/<topic>/<slug>.md` checks only the selected lead without writing, so unrelated legacy files do not block it. Omit the path to check all procedures; full audit remains collection-wide and fails for incomplete legacy files. Without Python, compare against the Procedure File template: risk read-only/changes-state, real nonfuture approved/verified dates, Active memory with Trigger, Prerequisites, numbered Steps, Verify, Related and Notes; changes-state also needs Approval and Recovery. Empty sections and fenced examples do not count. Structure does not prove truth, owner approval, success or permission. Read incomplete legacy procedures as evidence only; ask the owner to repair and verify before executing.

**Defining one** ("let's define a procedure for X"):

1. Read `memory/workflows/index.md`. If a procedure or workflow already covers X, propose changes to that file instead of a new one.
2. State the current understanding and recommended procedure first. Ask only questions whose answers change the procedure: the trigger, where things are, defaults, then each step with its exact command or click. Mark each point where the owner must say yes as a ready check.
3. Run the steps for real with the owner. A procedure holds only steps that were run and verified; when the run has to wait, say so, and save after that run.
4. Before changing an existing procedure, apply Recovery before editing. Pick a topic from `memory/schema.json` (a new topic only with the owner's OK). Show the owner the full file and save only after a clear yes.
5. Add a `memory/rules.md` row whose When is the trigger and whose Lead is procedure `memory/workflows/<topic>/<slug>.md`. Run `indexes.py`, then `gate.py audit`; stop and report any owner-repair-only findings instead of inventing dates or looping. Commit in a git repo only after required checks pass.

**Following one:** open the matching file and run its steps in order, stopping at each ready check until the owner says yes. When a step fails or no longer matches the system, stop and propose the change; edit the file only after the owner's yes.
