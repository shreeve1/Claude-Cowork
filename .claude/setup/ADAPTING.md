# Making it fit the owner

Three steps: settle the tracking model (what the owner needs remembered), make it run under the owner's agent app and machine, then make it fit how the owner works. The tracking model comes first and before filing old notes, so migrated facts have a home. Do part 1 before part 2. Run the tracking model and part 2 through the `talk-it-through` skill. For an underspecified opening, use its one open question; then state the understanding and recommendation, make routine defaults, and ask only a question whose answer changes the direction.

## Tracking model (before filing old notes)

Follow `.claude/skills/memory-setup/tracking-model.md`.

Memory edits preserve verified previous content in `.memory-recovery/` even without Git. Without Python, the agent must copy and verify with file tools and disclose manual-only checks; if verification is unavailable, it stops. Recovery may contain sensitive summaries; it is ignored, not encrypted. Release copies exclude it; upgrades retain the old workspace and copy recovery separately only with owner approval.

## Part 1: harness and machine

This workspace was written for a terminal coding agent that reads `CLAUDE.md` at the workspace root and loads skills from `.claude/skills/<name>/SKILL.md`. The owner may use a different desktop or terminal agent.

1. Find out which agent app the owner uses and how it loads instructions. Many read `CLAUDE.md`; some read another file name (for example `AGENTS.md`) or need a setting. If needed, add a short file that points at `CLAUDE.md`; do not copy and fork it.
2. Find out where that app looks for skills. If it does not read `.claude/skills/`, configure it to, or link that folder to the expected place. Keep `.claude/skills/` as the real copy so updates keep working.
   For an app that loads skills only from its own saved list, this is the install step in `README.md` ("Skills in the owner's app").
3. Note anything that does not fit (a command the app lacks, a path that differs) and tell the owner. Shipped files stay as shipped; the fix goes into a pointer file, the app's own settings or a preference note.

## Part 2: how the owner works

Start by recommending a setup from what the owner has already said. Use these questions as territory, not a checklist: ask only the next question whose answer changes the setup, skip answered points, and state obvious defaults.

1. **What do you mostly use an agent for?** Writing, research, IT support, coding, planning, something else. This decides which skills matter.
2. **Which skills will you not use?** List the skills under `.claude/skills/` with one line each. Do not delete shipped skills; the check fails without them. Instead add a row to `memory/rules.md` (When: Always, Note: "never use skill `<name>`") so the agent leaves it alone.
3. **How should answers read?** Length, tone, bullets or prose, language. Save the answer as a preference note with `personal-memory` and add a row to `memory/rules.md`. Do not edit `CLAUDE.md` for this: a preference note never conflicts with an update.
4. **Where should files go?** Show `memory/preferences/document-scaffolding.md` (the folder map). Change it to the owner's folders. It is the owner's file and updates leave it alone.
5. **Who and what do you refer to by short names?** People, companies, systems. Add each to `memory/glossary.md`. The things settled in "Tracking model" are already there.
6. **Which words do you use in a specific way?** Add them to `CONTEXT.md` through `talk-it-through`.
7. **Which rules in `CLAUDE.md` do not fit?** Read the headings with the owner. Never edit `CLAUDE.md`: write a preference note that overrides the rule, with a row in `memory/rules.md` (When: Always). The note wins because it is loaded for every task.
8. **Do you want a start-of-day routine?** See "Start-of-day loop" below.
9. **Do you have meeting transcripts?** If a transcription tool (Teams, Zoom, Otter, Granola, a recorder app) saves transcripts to a folder, personalize the `meeting` skill now: ask its "First use" questions (`.claude/skills/meeting/SKILL.md`) and save the answers in `memory/preferences/meetings.md`. Run it once on a real transcript with the owner. If there are no transcripts, leave the note as shipped and say the skill is there when they start recording.
10. **What must the agent never do?** Systems never to touch, people never to contact, actions that always need asking. Save as a preference note with a row in `memory/rules.md` (When: Always).

After the interview, restate the answers as a short list, ask "Is anything here wrong?", then make the changes and commit with the owner's OK.

## What survives an update

An update is a fresh copy of the new version with the owner's content brought across (`README.md`, "A newer version arrived").

| What | On an update |
|---|---|
| Memory notes, `memory/index.md`, `memory/rules.md`, the glossary, `CONTEXT.md`, the folder map, the owner's own skills, documents | Copied across whole. |
| Shipped files (`CLAUDE.md`, shipped skills, these docs) | Replaced by the new version. Never put personal content in them. |
| A rule that overrides a shipped one | Kept: it lives in a preference note. |

## Start-of-day loop

Run the `startday-spec` skill with the owner through `talk-it-through`. It picks the modules (work items, meeting transcripts, watched files or pages), the runner (none, a local scheduled task in Claude Desktop or Codex, Claude Code `/loop`, omp `/loop`) and writes `.claude/startday.json`. Cowork and other cloud schedulers run remotely by default and cannot see this folder; `startday-spec` explains when a local run works.

The loop is optional. With no runner the owner types `startday` when they want a run, and nothing else changes.

Do not treat any of this as working until the owner has run it once.
