---
name: startday-spec
description: |
  A spec for building or tailoring your own start-of-day loop. It starts from your calendar: an agent that plans the day around your fixed events, briefs you before meetings, gathers your work items, meeting transcripts and watched files or pages, researches each read-only, drafts every change as an approval you tick, and executes only what you ticked. Fixed rules, optional modules (including a weekly look-back that saves a lesson you taught more than once), a choice of runner (none, scheduled task, or loop) and a short interview that turns it into a skill fitted to your tools.

  Use when the owner wants a start-of-day routine, a "work my queue" loop, asks to set up or adapt startday, or wants it to run on a schedule. Run it through the talk-it-through skill; it does not run a day by itself.
---

# startday-spec

This is not a working loop. It is the recipe your agent follows, together with you, to write or tailor your own `startday` skill.

## When to use

- You want an agent to prepare your day: read today's calendar and brief you before meetings, pull your work items, process meeting transcripts, watch files or pages, and line up the changes for you to approve.
- You want startday to run by itself during the day (a scheduled task or loop) instead of typing it.
- You already have `startday` and your tools changed. Rerun the interview; keep what still fits.
- You want a weekly look-back that turns feedback you gave more than once into memory (`references/modules.md`, "Look-back").


## How to run

1. Read `references/core.md`. Its six rules are fixed. The interview may shape everything else, never these.
2. Start the `talk-it-through` skill with this spec as the plan under discussion. Ask the questions in `references/interview.md` one at a time, each with a recommended answer. Skip any the owner already answered.
3. Fill in `references/skeleton-SKILL.md` with the answers, keeping only the modules the owner picked (`references/modules.md`). Replace every `<fill in>` marker; leave the rest of the wording alone unless an answer forces a change. A blank or "not sure" answer counts as not answered: ask again or use the recommended default and say so.
4. Pick the runner with the owner from `references/runners.md`, then work through `references/adaptation-list.md` for the owner's harness and machine. Write down what you found and what you chose.
5. Show the owner the finished skill and `.claude/startday.json` in full. Ask before writing anything. Only after a clear yes, write the skill to `.claude/skills/startday/SKILL.md` and the settings file. Never overwrite an existing `startday` without showing the differences and getting a second yes.
6. Tell the owner the next step plainly: try it on a test system or a test day before a first real day, and only then turn on the runner.

## The six rules

See `references/core.md`. In short: research is read-only; every change is an approval the owner ticks; the loop never waits on the owner; each item has a research file with a Path to Close; the owner's text always survives; blank answers are not answers.

## Words used

- **Work item**: one thing the owner works on to completion (a ticket, an email thread, a task, a project). The interview defines it.
- **Module**: one feed into the day: calendar, work items, meetings or watch. The core runs whichever the owner picked.
- **Look-back**: a weekly review of the owner's feedback. It saves a lesson to memory only when the owner taught it in 3 or more independent signals; otherwise it logs a candidate.
- **Fixed event**: a calendar event the owner must attend at its time. A **flexible** event is the owner's own block, worked whenever fits.
- **Brief**: a short note the agent writes before a fixed event: who, why, linked items, last notes, open promises.
- **Runner**: what starts the next run during the day: nobody (the owner types it), a scheduled task, or a loop.
- **Research file**: one document per work item where the agent writes what it found.
- **Path to Close**: the section of a research file that says what is still needed to finish the item, who does each step, and the next drafted change.
- **Approval**: a drafted change with a checkbox. Nothing happens until the owner ticks it.
- **Parked**: an item waiting on someone or something. The loop moves on and checks it again later.
