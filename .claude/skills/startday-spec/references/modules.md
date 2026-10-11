# Modules

The core (the six rules, research files, approvals, questions, wrap-up) is always on. Modules are what feeds it. The owner picks any mix; each picked module adds its section from the skeleton. A module left out leaves no trace in the finished skill.

Work items, Meetings and Watch write only research files, the approvals page and questions (Meetings also saves facts to memory with `personal-memory`). Look-back is not a feed: it reviews what the owner's feedback taught across many days, and writes memory only through `personal-memory`. The six rules cover all four unchanged.

## Work items

Things the owner drives to completion: tickets, tasks, email threads, projects. Interview questions 1 to 3 define them. Each gets a research file with a Path to Close.


## Meetings

Turns finished meeting transcripts into facts, decisions and drafted follow-ups.

- **Source:** a folder the owner's transcription tool saves to (Teams, Zoom, Otter, Granola and others can export or sync to a folder). Watched with `scripts/watch.py`, or by hand when Python is missing (see "Watching without Python"), as a `path` target with `"use": "meetings"`. A tool that only keeps transcripts online needs a connector the agent can read; otherwise this module is not available.
- **Per transcript, write a meeting record** in the research folder: date, who attended, a short summary, decisions, the owner's own commitments, other people's action items, and open questions.
- **Facts** worth keeping go to memory with the `personal-memory` skill, each with the meeting as its source.
- **Follow-ups** (an email to send, a task to create, time to book) are drafted as approvals on the matching work item's research file, or on the meeting record when no item matches.
- **Who it belongs to** is only a guess until the transcript itself names the person, company or item. When unsure, add a question ("Is the meeting on <date> about <item>?") and keep the facts in the record until it is answered.
- A transcript still being written is not read: `watch.py` waits until the file has not changed for two minutes.

## Watch

Tells the owner when a file, folder or web page they care about changes, and what changed.

- **Targets:** each `path` or `url` in `.claude/startday.json` with a one-line `why` ("new contracts", "vendor outages"). Local folders and pages that load without signing in. A page behind a sign-in needs a connector or the browser, not `watch.py`.
- **Each change:** read it, decide whether it matters for the `why`, and write one line to the activity log or the related research file. A change that needs an action becomes a drafted approval, never an action.
- **Pages** are compared by visible text, so a redesign can show as a large change with nothing new in it; say so instead of reporting it as news.
- **A target that cannot be read** is reported as an error each run it fails and keeps its last good copy, so nothing is lost.

## Look-back

Saves a lesson only when the owner taught it more than once. It reads the research files and approvals the other modules wrote, about once a week.

- **When:** at most once every 7 days: on the first run after the start time that finds no `Look-back done` line in the activity log from the last 7 days.
- **Window:** every pass re-reads all owner feedback from the last 90 days, not only what is new since the last pass, so one correction a week can still reach three. A signal is used up, and not counted again, when a memory note lists it as a source or states the lesson and is newer than the signal.
- **Owner feedback lines:** on every run, when Check approvals finds a `[-]` rejection or an edited body, add one line to that item's research file under Findings: `Owner feedback <date>: rejected A-012: "<the owner's reason, in their words>"` or `Owner feedback <date>: edited A-012: "<before>" -> "<after>"`. Write it once per approval id: when the file already has an `Owner feedback` line for that id, add nothing, so a rejection seen on two runs is one signal. A correction the owner gives in chat while the agent works on an item is logged the same way, once per correction. One that belongs to no item goes in the activity log. Use the owner's words, never the agent's reading of them.
- **Reads:** the `Owner feedback` lines in the window, and the owner's `Notes` and `Answers` in research files changed in the window. It does not read chat history or transcripts: not every app keeps them.
- **Leads, not evidence:** a reason the agent wrote itself (voided, superseded, stale, left the queue) says where to look, never what the owner prefers. Ten voids that follow one owner statement are one event, not ten.
- **Independent signals:** two signals are independent when they are different owner actions on different approvals or items, each with its own reason. Redrafts that follow one owner statement are one signal.
- **3 or more independent signals with the same lesson:**
  1. Look for a memory note that already states it. If one does, write nothing and log `rule exists, drafts still missed it: <note path>`.
  2. If none does, write the note with the `personal-memory` skill. List the item ids and dates as its source. A note that contradicts an older one replaces it in place, as `personal-memory` says.
  3. Make sure something loads the note: add or update the row in `memory/rules.md` that reaches it (`personal-memory` "Rules"). A note nothing loads changes nothing.
- **1 or 2 signals:** a candidate. One line in the activity log, no note. The signals stay in the research files, so the next pass counts them again together with any new ones.
- **Log:** `Look-back done <date>: wrote <n>, candidates <n>`, then one line per candidate.
- **Scripts:** none. Writing a note follows `personal-memory`, including its no-Python path, so Look-back runs where Python cannot be installed.


## `scripts/watch.py` contract

- `python3 .claude/skills/startday-spec/scripts/watch.py [--config <file>] [--state <file>]`, defaults `.claude/startday.json` and `.claude/startday.state.json`. `watch.py --ack` clears the pending changes.
- Config: `{"watch": [{"path": "...", "use": "meetings", "why": "..."}, {"url": "https://...", "why": "..."}]}`. Each entry has exactly one of `path` or `url`; `~` is expanded.
- Prints a JSON list; each change has `target`, `use`, `why`, `change` (`new`, `changed`, `gone`, `error`) and `file` + `sha256` + `id` (paths), `diff` (pages, up to 40 lines) or `detail` (errors). `id` is fixed per file path, so a transcript edited later keeps its `id`. Exits 0, or 1 on a missing or bad config.
- A change stays pending and is printed every run until `--ack`. Run `--ack` only after every printed change is written down, so a run that stops halfway loses nothing. A file still `new` to the agent stays `new` if it changes again before the ack. Errors are printed each run they happen and never pending.
- The first run of a target records a baseline and reports nothing. The state file is the owner's runtime data: keep it out of git.
- Standard Python only; it reads targets and writes only its state file.

## Watching without Python

Use this when `python3 --version` fails, so `watch.py` cannot run. It does by hand what `watch.py` does and reports the same kinds of change. It is less exact (size and modified time instead of a content hash) and costs more tokens each run.

- **State:** the `"manual"` key of `.claude/startday.state.json`; create the file as `{}` when it is missing. Never touch its other keys. Shape: `{"manual": {"files": {"<target path>": {"<file path>": "<bytes>:<modified time to the second>"}}, "pages": {"<url>": "<visible text>"}, "pending": {"<file path or url>": {"change": "new|changed|gone", "target": "...", "use": "...", "why": "..."}}}}`.
- **Folders:** list every file under each `path` target, skipping names that start with a dot, with its size and modified time. The first time a target is seen, store them as the baseline and report nothing. After that, a file not stored is `new`, one with a different size or time is `changed`, and a stored file that is missing now is `gone`.
- **Still being written:** a file modified in the last 2 minutes is not read. Keep its old stored value (store nothing if it is new) so a later run reports it.
- **Pages:** read the visible text of each `url`, without scripts or styles. The first time, store the text (at most 20,000 characters) and report nothing. After that, when it differs, report `changed` with the changed lines (at most 40) and store the new text. A redesign can look like a large change with nothing new in it; say so.
- **Pending:** store each detected change in `manual.pending` at once, one entry per file or url, together with the updated `manual.files` or `manual.pages`. A `new` file that changes again stays `new`. Once every pending change is written down, clear `manual.pending`; until then the next run lists them again. A target that cannot be read is an `error`: log it each run it fails, never make it pending, and keep its stored value.
- **Ids:** name a meeting record from the file name: lowercase, each run of other characters replaced by `-`, no extension (`2026-10-09 Supplier call.txt` becomes `2026-10-09-supplier-call`). If another file already owns that name, add `-2`. These ids differ from `watch.py`'s, so switching a folder between the two methods can reprocess a transcript once.
