---
name: personal-memory
description: Use when capturing, promoting, pruning, or using local personal memory under memory/. Triggers include remember this, capture this preference, run memory check, email preferences, voice preferences, glossary or entity shorthand, client facts (Client Memory, client hubs), defining or following a procedure ("let's define a procedure for X"), and important docs to remember.
---


# Personal Memory

Use this skill to operate the local `memory/` workspace memory system. In a project it holds what a future session would otherwise re-learn: decisions, gotchas, how the project's stack is set up, and the owner's preferences for working in it; in a personal workspace, also preferences and durable personal context. Facts the project's own docs or code already state are linked, not copied.

## Scope

`<skills>` below is the folder that holds this skill's folder: `.claude/skills` in a workspace or a project copy, `~/.claude/skills` for a global install. In the commands below, `python3` means `python` where that is the working command (often on Windows).

Memory lives in `memory/` at the folder root. Scripts live in this skill's folder; run them from the folder root as `python3 <skills>/personal-memory/<script>.py`. Git is optional. When the folder is a git repo, memory `.md` files are tracked so they have history, and binaries and `memory/raw/` are git-ignored; never store credentials, since history keeps them and travels with any push. When it is not a repo, memory works the same with no history. Hooks run only where the workspace enables them; otherwise run `gate.py audit` directly.

## Safety Rules

- Never store secrets, tokens, passwords, API keys, bearer strings, OAuth credentials, or credential-like config. Omit them automatically, note the omission (in the commit message, or in the reply when there is no repo), and never ask.
- Client and third-party information (client names, environments, contacts, config facts) IS allowed — it is what makes memory useful. Only credentials are excluded. Exception: Ticket Guides in `memory/guides/` keep their redaction rules (no client names, user emails, hostnames, IPs, tenant IDs, raw logs, or full ticket text).
- Prefer short summaries over raw content. Do not store full emails, screenshots, client documents, or transcripts by default.
- Use `memory/raw/` only when the user explicitly asks to keep raw material.
- Strip credentials from anything written, including raw material.

## Memory Read Policy

Reads are routed by `memory/rules.md`; the session-start steps live in the folder's `CLAUDE.md` (or `CLAUDE.md`) "DO THIS FIRST". Inside this skill:

1. Treat index rows as pointers, not facts: open the linked file before relying on or acting on a row.
2. Client skills read Client Memory through the hub `memory/<client_folder>/_hubs/<short>.md`, never by guessing note paths.
3. Before wrapping up, run the end-of-session sweep (see Global Capture).
4. If a note you rely on is older than 90 days (`updated` or `verified`; `gate.py stale` lists them), re-ground it against current tool output or files first. Update it in place, or delete it if no longer true. Do not ask the user.

## Rules

`memory/rules.md` is one table: When | Lead | Also load | Note. A rule is a trigger plus pointers; the content it points to lives in a preference, email, workflow or other memory file.

- Add a row when the owner says to remember something as a rule ("when X, use Y"), or when a new preference or email file is written: every file in `memory/preferences/` and `memory/email/` must be reachable from a row.
- Lead holds at most one skill, the one that runs the workflow. Also load holds files and skills that only add content. Write skills as skill `name` (found in the project's skills folder, the global skills folder, or next to this skill) and paths backticked, folder-relative.
- A plain "always do X" goes in the content file it governs; if none fits, write a preference file and add it to the Always row.
- Edit an existing row before adding a near-duplicate. No rationale in rows; put it in a decision note.
- After editing, run `gate.py audit`; it fails a row naming a missing skill or file, and any preference or email file no row reaches.

If `memory/index.md` does not exist, proceed normally and create it only when writing the first promoted memory item.

Read tolerantly. Never refuse to use a memory file because of missing optional frontmatter fields, an unknown `type`, extra unrecognized keys, a missing `index.md`, or a broken cross-link. Do best-effort consumption; a broken link may just be not-yet-written memory.

## Cross-linking

Memory topics may reference each other with standard markdown links.

- Use workspace-relative paths starting with `memory/`, for example `[email tone](memory/email/tone-and-format.md)` — the same base `memory/index.md` uses.
- A link asserts a relationship; the kind lives in the surrounding prose. Add related links under a `## Related` heading when a topic depends on or informs another.
- Every note you write links to the 1-3 existing notes it depends on or informs, and says how in the same line. Find candidates with `gate.py backlinks <path>` on the likeliest neighbour, and by reading its hub or topic index. Read the target note before writing the reason: the reason states only what both notes say, never what only the source says. Link outward only; never edit the target to link back, because A→B already gives B its backlink. A note with nothing to link to is fine: do not invent a link.
- Backlinks ("Cited by") are not stored in files. `python3 <skills>/personal-memory/gate.py backlinks memory/<path>.md` computes them by reversing the link graph. Run it before changing or deleting a note to see what depends on it.
- `gate.py links` reports broken links, notes with no outgoing links and notes nothing links to. The two isolation lists ignore links from indexes and hubs, since those list every note; `backlinks` shows them, because deleting a note breaks them too. `gate.py audit` warns on broken links but never fails on them.

## No Candidates

There are no memory candidates and no approval step for memory writes (a `memory/candidates/` folder, if present, is not part of this system and is not audited). Memory is written autonomously when a capture trigger fires. The guards are checks, not questions: the Safety Rules, the Conflict Resolution rule (overwrite in place; in a repo, git keeps the old text), the grounding rule, and `gate.py audit`.

## Reference file

For setup or migration, use the `memory-setup` skill. Recovering missing scaffold (`README.md`, `TEMPLATES.md`, `index.md`), a full memory-health lint, Client Memory, the Weekly Sweep and Procedures are in `<skills>/personal-memory/reference.md`; open it only for one of those. Saving a preference, doc, workflow or decision needs nothing in it. The directory layout, data classes and file naming are in `memory/README.md`.

## Global Capture

Watch for capture triggers in every meaningful session, not only when the user says "remember this." Check for them once, at the end of each task:

- The user corrects you or overrides something you did.
- The user states a rule or preference about how to work ("always…," "never…," "we use X for Y," "keep it to…").
- The user describes how a process or workflow goes, or sets a boundary on one.
- A decision is settled that a future session would otherwise re-litigate.
- You discover a non-obvious fact likely to come up again (a fix, a gotcha, a tool quirk, how their stack or a client's environment is set up) that a future session could not cheaply rediscover.

Write everything that qualifies once, at the end of the task, per the Capture Workflow below — not mid-task after each trigger. Do NOT ask first and do NOT append an "ask to remember" footnote.

End-of-session sweep: before wrapping up meaningful work, capture what qualifies, then give the report (see Output Rules). If nothing qualified, say: `Memory check: nothing worth capturing.`

Do not capture one-off task details (a single ticket, user, record, or device), the status of work still in motion (save it once, when it settles), temporary instructions, facts memory already states correctly, guesses about personality, or credentials.

Exceptions:

- `<client_folder>/<short>/tickets/`, `<client_folder>/<short>/projects/`, `<client_folder>/<short>/meetings/` and `<client_folder>/<short>/procedures/` (workspace root) are documents, not memory. The one-off / work-in-motion exclusion does not apply to them. Lasting facts found there still get copied into Client Memory.
- Temperature carve-out: a dated, sourced observation of what pleased or frustrated a client (for example "2026-10-07, #70474: asked for fewer status emails") goes to `memory/<client_folder>/temperature/<short>/`. A character judgement ("Ed is impatient") is still a personality guess and is never stored.

## Capture Workflow

Runs autonomously at the end of each task. It never asks the user. Only ask when the user's own request is ambiguous about what to do, never to get permission to write memory.

Grounding: write only what the session actually showed (tool output, file contents, or the user's own words). Do not store guesses. If a fact is plausible but not observed, either omit it or mark it `unverified` in Notes.

Omit automatically (note the omission in the commit message or the reply, never ask):

- Credentials of any kind (see Safety Rules).
- Raw material the user did not explicitly ask to keep.
- Ticket Guides: never auto-write to `memory/guides/`. Otherwise route a guide-shaped item to `memory/workflows/<topic>/` or `memory/docs/` as a redacted note.

If the target file is unclear, pick the closest existing topic file by `memory/index.md` row and note the choice in the commit message or the reply. Do not store a rule you cannot place.

Direct promotion steps:

1. Read `memory/index.md` if it exists.
2. Read only promoted topic files needed to detect conflicts or merge into the right category.
3. Write or update the appropriate promoted topic file under:
   - `memory/preferences/`
   - `memory/docs/`
   - `memory/voice/`
   - `memory/email/`
   - `memory/guides/` — never auto-written here.
   - `memory/workflows/<topic>/<slug>.md` — pick a topic from the `topics` list in `memory/schema.json` (a new topic only with the owner's OK). Shared Procedures (`type: procedure`) here are written only through an owner-approved change, never auto-captured. Defining or following one: Procedures in `reference.md`. After writing, run `indexes.py` and `gate.py audit`.
   - `memory/decisions/<topic>/decision-<slug>.md` — same topic list; after writing, run `indexes.py` and `gate.py audit`.
   - `memory/<client_folder>/<subject>/<short>/<slug>.md` — Client Memory, for lasting facts about one client. See Client Memory in `reference.md`. After writing, run `python3 <skills>/personal-memory/hubs.py`; add an `index.md` row under `## Client Hubs` for any new hub.
   - `memory/glossary.md` — entity directory (shorthand -> identity). Route here for plain label expansions; contested/overloaded terms go to `CONTEXT.md` instead. When first created it gets its OWN `index.md` row for discoverability; `gate.py audit` audits promoted folders and Client Memory, not root files, so it will not flag a missing glossary row. Internal format: see the `glossary.md` template in `memory/TEMPLATES.md`.
   - `memory/rules.md` — a rule (trigger plus pointers), and a row for any new preference or email file. See Rules.
4. Update frontmatter to `status: promoted` where relevant.
5. Create or update `memory/index.md` with the promoted row. Carry the file path either backticked (`` `memory/decisions/<topic>/decision-x.md` ``) or as a markdown link (`[title](memory/decisions/<topic>/decision-x.md)`) so `gate.py audit` can recognize the entry.
6. Run `python3 <skills>/personal-memory/indexes.py` (regenerates the two topic sub-indexes; skip if no workflow/decision changed), then `python3 <skills>/personal-memory/gate.py --memory memory audit`. If audit fails, apply the safe deterministic fixes (add missing index rows, remove stale rows, fix topic placement), then re-run until it exits 0. If it prints a size, summary or history warning for a file you touched, trim that file now (see Keep Memory Lean).
   **No Python** (`python3 --version` fails, as in many enterprise environments): skip both scripts and do their work by hand. Add the `memory/index.md` row from step 5. For a workflow or decision, also add one line under its topic heading in `memory/workflows/index.md` or `memory/decisions/index.md`, written like its neighbours: `- [Title](<path>) summary (date)`. Then re-read what you wrote and confirm each thing the audit would check: every path in the new index row and in any `memory/rules.md` row exists, a skill named in a row exists in the project's skills folder, the global skills folder, or next to this skill, a preference or email file is named by a `rules.md` row, the note has frontmatter like the other notes in its folder with a `summary` of at most 160 characters, and the note is at most 6144 bytes. Say in your reply that the audit was not run.
7. If the project is a git repo, commit the memory files you wrote with the task's commit (or on their own as `memory: <what changed>`), with a body line for any omission or placement choice; stage only memory files you wrote. Read history with `git log -- memory/`. If it is not a repo, the capture ends after the audit.
8. Report per Output Rules.

## Client Memory

Before writing or reading a client fact, read Client Memory in `<skills>/personal-memory/reference.md`: note paths, required frontmatter, subjects and hubs.

## Procedures

When the owner says "let's define a procedure for X", or a task matches a saved procedure, follow Procedures in `<skills>/personal-memory/reference.md`.

## Conflict Resolution

- A new item that contradicts an existing rule replaces it in place: the file states only the current rule. In a repo, git keeps the old text.
- When the reason for the change will still guide future work, add one line under `## Notes`: `Changed YYYY-MM-DD: <why>`. Never keep the old rule's wording in the file.
- If the two rules could both hold (different scope or client), keep both and note the scope that separates them.

## Keep Memory Lean

`gate.py audit` warns; the task that touched a flagged file fixes it before finishing. Warnings never block a task, so another session's mess never stops yours.

- A note is at most 6144 bytes. Over that, cut narration, build logs, settled status and anything stated elsewhere (link instead); split a decision by topic only when every line is still current.
- `summary:` and each `memory/index.md` summary are at most 160 characters.
- No history in files: no `Superseded`, `Updated` or `Amended` lines. Overwrite in place; at most one `Changed YYYY-MM-DD: <why>` line per change, and only when the reason still matters.
- A note that is wrong or no longer useful is deleted, with its index row. A file with `status: superseded` is deleted the same way.
- Procedures follow the same rule: corrected in place.

## Weekly Sweep

Only where a scheduled sweep is set up (`WEEKLY-SWEEP.md` in a starter workspace) or the owner asks: follow Weekly Sweep in `<skills>/personal-memory/reference.md`.

## Output Rules

- After capturing, end the reply with one line per item: `Memory saved: <path> - <short summary>`.
- Mention any automatic omission in one line, without echoing the omitted content (for example, `Omitted: credential in tool output`).
- If nothing qualified at wrap-up, say `Memory check: nothing worth capturing.`
- Keep memory notes short and operational.
