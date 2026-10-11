# Making it fit the owner

Three steps: settle the tracking model (what the owner needs remembered), make it run under the owner's agent app and machine, then make it fit how the owner works. The tracking model comes first and before `MIGRATING.md`, so migrated facts have a home. Do part 1 before part 2. Run the tracking model and part 2 through the `talk-it-through` skill: one question at a time, each with a recommended answer, and the owner decides.

## Tracking model (before MIGRATING.md)

Every owner has people or things they keep coming back to and need remembered in a steady shape: clients, students, patients, properties, customers, projects, a team. This workspace stores them as Client Memory: one short name per thing in `memory/glossary.md`, one small note per lasting fact (subject, verified date, source), a generated hub per thing, and a row in `memory/rules.md` that loads the hub when the agent works on it. The shipped words say "client". The owner's own word goes into the folder name (`client_folder` in `memory/schema.json`) and into `CONTEXT.md`, so it reads naturally to them.

Ask: **"What people or things do you keep coming back to, and what do you need remembered about each?"** Skip if the owner already answered.

If the owner has such things:

1. Note the owner's word for them (for example "student") and turn it into a folder name: one lowercase word, usually plural (`students`). Set `"client_folder": "students"` in `memory/schema.json`. The key is optional and defaults to `clients`; the memory scripts, the commit hooks and the audit all follow it. Set it before any note exists. If `memory/clients/` or `clients/` already holds files, first move both folders to the new name with `git mv`, run `python .claude/skills/personal-memory/hubs.py`, and fix the hub rows in `memory/index.md`. Exception: if `.claude/skills/startday/` exists, leave `client_folder` unset; startday and the shipped Procedures use `clients/`.
2. Add each thing to `memory/glossary.md` as a short name plus identity, in a table under a `## Clients` heading. Keep the heading `Clients` whatever the owner's word; scripts read it.
3. Propose 3 to 6 subjects, the kinds of lasting facts the owner named (for example `contacts`, `preferences`, `history`). Lowercase single words. With the owner's OK, add them to `client_subjects` in `memory/schema.json`. Keep every subject already listed there and every subject an existing note uses; only add. Remove one only after its notes are moved to another subject or the owner agrees to drop them, otherwise the audit fails. Leave `client_dirs` as shipped unless the owner wants fewer document folders.
4. Add a `CONTEXT.md` entry saying the owner's word means Client in this workspace (`talk-it-through` keeps it).
5. `memory/rules.md` ships with a row `Work on one client` that loads `memory/clients/_hubs/<short>.md`. Change its When to the owner's word and its path to the folder from step 1 (`memory/<client_folder>/_hubs/<short>.md`).
6. In `memory/preferences/document-scaffolding.md`, add `<client_folder>/<short>/` to the folder map: documents about one thing, in the subfolders `client_dirs` lists.
7. Prove it: with `personal-memory`, write one real note for one thing and run `hubs.py`. Add the new hub's row under `## Client Hubs` in `memory/index.md` (the audit fails a hub without one), then run `python .claude/skills/personal-memory/gate.py --memory memory audit` and show the owner the hub. Without Python, write the hub row by hand and skip the audit.

If the owner has no such things: leave `client_subjects` empty, delete the `Work on one client` row from `memory/rules.md`, tell the owner why, and skip steps 1 to 7. If they track some other kind of thing (projects, topics, a household), treat that as the thing and follow the steps above. Revisit this section whenever the owner's work changes.

## Part 1: harness and machine

This workspace was written for a terminal coding agent that reads `CLAUDE.md` at the workspace root and loads skills from `.claude/skills/<name>/SKILL.md`. The owner may use a different desktop or terminal agent.

1. Find out which agent app the owner uses and how it loads instructions. Many read `CLAUDE.md`; some read another file name (for example `CLAUDE.md`) or need a setting. If needed, add a short file that points at `CLAUDE.md`; do not copy and fork it.
2. Find out where that app looks for skills. If it does not read `.claude/skills/`, configure it to, or link that folder to the expected place. Keep `.claude/skills/` as the real copy so updates keep working.
3. Re-verify the shipped structure against "What must be true" in `MIGRATING.md` and fix what fails.
4. Note anything that does not fit (a command the app lacks, a path that differs) and tell the owner. Shipped files stay as shipped; the fix goes into a pointer file, the app's own settings or a preference note.

## Part 2: how the owner works

Ask these in order. Skip any the owner already answered. Stop early when the rest have obvious defaults, and say which default you used.

1. **What do you mostly use an agent for?** Writing, research, IT support, coding, planning, something else. This decides which skills matter.
2. **Which skills will you not use?** List the skills under `.claude/skills/` with one line each. Do not delete shipped skills; the check fails without them. Instead add a row to `memory/rules.md` (When: Always, Note: "never use skill `<name>`") so the agent leaves it alone.
3. **How should answers read?** Length, tone, bullets or prose, language. Save the answer as a preference note with `personal-memory` and add a row to `memory/rules.md`. Do not edit `CLAUDE.md` for this: a preference note never conflicts with an update.
4. **Where should files go?** Show `memory/preferences/document-scaffolding.md` (the folder map). Change it to the owner's folders. It is the owner's file and updates leave it alone.
5. **Who and what do you refer to by short names?** People, companies, systems. Add each to `memory/glossary.md`. The things settled in "Tracking model" are already there.
6. **Which words do you use in a specific way?** Add them to `CONTEXT.md` through `talk-it-through`.
7. **Which rules in `CLAUDE.md` do not fit?** Read the headings with the owner. Never edit `CLAUDE.md`: write a preference note that overrides the rule, with a row in `memory/rules.md` (When: Always). The note wins because it is loaded for every task.
8. **Do you want a start-of-day routine?** See "Start-of-day loop" below.
9. **What must the agent never do?** Systems never to touch, people never to contact, actions that always need asking. Save as a preference note with a row in `memory/rules.md` (When: Always).

After the interview, restate the answers as a short list, ask "Is anything here wrong?", then make the changes and commit with the owner's OK.

## What survives an update

An update is a fresh copy of the new version with the owner's content migrated in (`UPDATE.md`).

| What | On an update |
|---|---|
| Memory notes, `memory/index.md`, `memory/rules.md`, the glossary, `CONTEXT.md`, the folder map, the owner's own skills, documents | Copied across whole. |
| Shipped files (`CLAUDE.md`, shipped skills, these docs) | Replaced by the new version. Never put personal content in them. |
| A rule that overrides a shipped one | Kept: it lives in a preference note. |

## Start-of-day loop

Run the `startday-spec` skill with the owner through `talk-it-through`. It picks the modules (work items, meeting transcripts, watched files or pages), the runner (none, a local scheduled task in Claude Desktop or Codex, Claude Code `/loop`, omp `/loop`) and writes `.claude/startday.json`. Cowork and other cloud schedulers run remotely by default and cannot see this folder; `startday-spec` explains when a local run works.

The loop is optional. With no runner the owner types `startday` when they want a run, and nothing else changes.

Finish with `CHECKLIST.md` on a test system. Do not treat any of this as working until the owner has run it.
