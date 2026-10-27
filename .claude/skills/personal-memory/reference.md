# Personal Memory Reference

Rare operations for the `personal-memory` skill: recovering missing scaffold, linting memory health, Client Memory, the weekly sweep and procedures. `SKILL.md` covers everyday capture and reads; open this file only for one of these. `<skills>` is defined in `SKILL.md`.

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
3. Act on what they show:
   - `status: superseded`, or a note whose only content is history: delete it and its index row.
   - Stale (over 90 days): re-ground it against current files or tool output. Still true: set `updated`. False: delete it. Needs a live system you cannot reach: leave it and name it in the report. Never delete a note for age alone.
   - Two notes on the same subject: merge into one, delete the other, repoint links (`gate.py backlinks <path>` lists them).
   - Over size, or a glossary row longer than one line: trim it and move the detail into a Client Memory source note (`memory/clients/<subject>/<short>/<slug>.md`), never into a hub, which `hubs.py` regenerates. Run `gate.py compact` only when `rules.md`, `glossary.md` and `index.md` are all clean in `git status`; it rewrites every padded one of them. Otherwise leave the padding and say so.
   - Crowded folder: consolidate per the 15-file rule.
4. Run `indexes.py --check` and `hubs.py --check`. If neither would change a file, skip to 5. Otherwise run `git status --short`: when every index or hub they would rewrite or remove is clean, run `indexes.py` and `hubs.py`; when one is dirty, leave it and name it in the report. Then `gate.py audit`; if it still fails only because of a file you were told to leave, report that and stop.
5. Commit only the paths this run changed or deleted, never other sessions' files: `memory: weekly sweep <date>`, with the swept and deleted paths in the body.
6. Reply with one line: files swept, notes deleted, merged, trimmed, left for the owner.

## Procedures

A procedure is a verified set of steps the agent follows whenever its trigger comes up: a `type: procedure` file in `memory/workflows/<topic>/<slug>.md`, shaped by "Procedure File" in `memory/TEMPLATES.md`. A runbook a person follows belongs in the project's `docs/` instead.

**Defining one** ("let's define a procedure for X"):

1. Read `memory/workflows/index.md`. If a procedure or workflow already covers X, propose changes to that file instead of a new one.
2. Interview the owner one question at a time: the trigger, where things are, defaults, then each step with its exact command or click. Mark each point where the owner must say yes as a ready check.
3. Run the steps for real with the owner. A procedure holds only steps that were run and verified; when the run has to wait, say so, and save after that run.
4. Pick a topic from `memory/schema.json` (a new topic only with the owner's OK). Show the owner the full file and save only after a clear yes.
5. Add a `memory/rules.md` row whose When is the trigger and whose Also load is the file. Run `indexes.py`, then `gate.py audit` until it exits 0, and commit in a git repo.

**Following one:** open the matching file and run its steps in order, stopping at each ready check until the owner says yes. When a step fails or no longer matches the system, stop and propose the change; edit the file only after the owner's yes.
