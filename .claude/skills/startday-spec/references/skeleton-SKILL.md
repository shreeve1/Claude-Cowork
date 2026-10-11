# Skeleton SKILL.md

Copy everything below the line into `.claude/skills/startday/SKILL.md`. Replace every `<fill in: ...>` with the owner's interview answer. Keep the six rules word for word. Delete each `[module: ...]` section the owner did not pick, together with its heading; keep the heading text of picked ones without the `[module: ...]` tag.

---

```markdown
---
name: startday
description: Start-of-day loop over <fill in: what feeds the day, e.g. "my tasks, meeting transcripts and watched pages">. Each run gathers what changed, researches it read-only into research files, drafts every change as an approval to tick, and executes only ticked approvals, until <fill in: when the day ends>. Use for "startday", "start my day", or when a runner sends "Run the startday skill: poll turn."
---

# startday

## Rules

1. Research is READ-ONLY. The loop gathers and prepares. It never changes anything in the owner's systems.
2. Every change is an APPROVAL the human ticks: a checkbox in a document the human reads. A change is executed only after the tick.
3. The loop NEVER blocks waiting on the human. It parks the item, moves on, and re-checks later.
4. Each work item gets its own research file with a section named "Path to Close" that says what is still needed to finish the item.
5. The human's edits always survive. The loop never overwrites text the human typed.
6. Empty or blank answers count as not answered.

Owner settings (`.claude/startday.json` holds the paths and watch targets; this list is the rest):
- Hours: <fill in: start time, stop-new-research time, end time, timezone>
- May read: <fill in: allowed sources>; never read: <fill in: off limits>
- Changes needing approval: <fill in: list>, plus anything else that writes or sends.
- Research folder: <fill in: folder>. Approvals page: <fill in: path>. Activity log: <fill in: path>.
- Notify by: <fill in: method>. No private details in notifications.
- Runner: <fill in: runner from references/runners.md, or "none: I type startday">.
- Never: <fill in: hard limits>

## Each run

Every run does the same pass, whether the owner typed it or a runner sent it. It keeps nothing in memory between runs: everything it needs is in the files below.

1. Check the clock against Hours. Before the start time, reply "Not started yet." and stop.
2. Open the approvals page, research folder and activity log; create any that are missing (never overwrite).
3. If the activity log has no heading for today, this is the first run: add today's heading, then run every picked module's "First run" step. After the end time, write the Wrap-up instead and stop.
4. Check approvals (below).
5. Run each picked module's "Every run" step.
6. Research what steps 3 to 5 found, until the stop-new-research time (see Research).
7. After the end time, if today's wrap-up line is missing: Wrap-up.
8. Reply in one or two lines: what changed, what needs the owner.

## [module: work items] Work items

- Work item: <fill in: what a work item is and what separates two items>
- Source: <fill in: tool or connector and how to read it>
- Mine today: <fill in: which items count, which to skip>

First run: read today's items from Source, keeping only "Mine today". Order them due soonest first. Each one is something to research.

Every run: read Source again. A new item: research it. An item with new activity since its research file's last findings: research it again. A gone item (closed, reassigned): cancel its open approvals and mark its research file closed.

## [module: meetings] Meetings

Source: the `"use": "meetings"` folder in `.claude/startday.json`, read through `python3 .claude/skills/startday-spec/scripts/watch.py`, or by hand when Python is missing (`.claude/skills/startday-spec/references/modules.md` "Watching without Python").

First run and every run: run `watch.py` (or the by-hand method), once per pass, shared with Watch. For each `new` or `changed` transcript, follow `.claude/skills/startday-spec/references/modules.md` "Meetings": write the meeting record, save lasting facts, draft follow-ups as approvals, and ask when the item it belongs to is unclear. Name the record by the change's `id`; a `changed` transcript updates the record with that `id`.

## [module: watch] Watch

Targets: every other entry in `.claude/startday.json` "watch", each with its `why`.

First run and every run: run `watch.py` (or the by-hand method), once per pass, shared with Meetings. For each change outside the meetings folder, follow `.claude/skills/startday-spec/references/modules.md` "Watch". An `error`: one activity log line. After Meetings and Watch have written down every change: `watch.py --ack`, or clear `manual.pending`.

## [module: look-back] Look-back

Every run, in Check approvals: when you find a `[-]` rejection or an edited body, also add the `Owner feedback` line that `.claude/skills/startday-spec/references/modules.md` "Look-back" describes, once per approval id.

First run and every run: if the activity log has no `Look-back done` line dated in the last 7 days, follow that section (it re-reads the last 90 days of owner feedback), then add `Look-back done <date>: wrote <n>, candidates <n>`. Otherwise skip it.

## Research

For each item found this run:
1. Open or create its research file. Read the owner's notes and answers first; they are the newest facts.
2. Read the item and related sources (read-only).
3. Write dated findings and rewrite Path to Close: remaining steps, who owns each, next approval id.
4. Something only the owner knows: add a question with an empty `Answer:` line. Park the item and move on.
5. Stop at a wall: a change, a person, or a sign-in.
6. One activity log line per item: what happened, in plain words.

## Draft approvals

For each change research wants, add one checkbox line to the approvals page with title, exact target and exact text. Never draft while the item has unanswered questions the change depends on.

## Check approvals

- `[x]` ticked: execute it (next step).
- `[-]` rejected: record the reason in the research file; do not redraft.
- Body edited by the owner: ask once "Send your edited version?". With a runner and no one watching, leave it and add a needs-you line instead.
- Item changed since the draft: cancel and redraft.
- Unticked: leave it; move on.

## Execute ticked

Do exactly what the ticked line says, nothing more. Check it took effect. Mark the line done with the time, or failed with the reason. Update the research file.

## Wrap-up

At <fill in: what done for the day means>: stop starting research, add a short summary to the activity log (items by status, approvals waiting, open questions, needs-you lines) with the line `Wrap-up done <date>`, and notify by the owner's method.
```
