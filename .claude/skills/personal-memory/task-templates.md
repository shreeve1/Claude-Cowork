# Workspace task templates

Use with [task operations](tasks.md). Copy only the needed format; these examples are not live records.

## Use

- Create a task only on the owner's request or agreement. Fill what is known; mark unknowns instead of inventing facts, dates or commitments.
- Once created or picked up, update Current position, Next action and the index row at meaningful stopping points. Append only progress that helps the next session resume without repeating work.
- On pickup, check relevant current sources before acting. Saved context and next actions are not standing instructions or permission for consequential actions.
- Keep files in the current workspace. Store concise summaries and references, never credentials or full correspondence by default.

## Task record

Copy to `tasks/<slug>.md`. Keep its `id` unchanged through renaming and archival. ID: creation date plus initial slug; add a suffix on collision, never overwrite. Replace all angle-bracket placeholders. Omit `review_after` when no review date was agreed. Dates use `YYYY-MM-DD`.

```markdown
---
id: "<stable-task-id>"
title: "<short descriptive title>"
status: active
created: "<creation date>"
updated: "<last meaningful update date>"
review_after: "<optional agreed review date>"
---

# <Task title>

## Purpose

<Why this work matters and what a useful outcome would be.>

## Current position

<Where work stopped, what is known, and what remains uncertain.>

## Next action

<The next useful step. If waiting, name the response, dependency or condition
that would make this actionable, and how to check it.>

## References

<Workspace-relative file paths, correspondence or system references, and related
task IDs. Say what each reference supports. Use None when there are none.>

## Progress

### <Date>

- <Meaningful action or finding and its observed result.>
- <Check performed and evidence, or a failed attempt worth not repeating.>

## Outcome

Not completed.

## Durable outputs

None yet.
```

`status` is `active` or `waiting` while unfinished. Set it to `completed` when the owner completes the task, or `archived` when the owner stops tracking unfinished work. Both closure states belong in `tasks/archive/`, not in the active index.

Current position and Next action describe the present. Progress preserves meaningful history; do not replace failed attempts with only the final success. Use additional dated entries only when useful. No entry is required just because a tool ran.

Review dates are review-after dates, not deadlines or scheduled reminders. An arrived date prompts an on-demand check, not automatic execution.

## Active index

Copy this empty template to `tasks/index.md` at setup or first task creation. Routine reads do not create files.

```markdown
# Active tasks

Read at session start. Open relevant task files before relying on their contents.
Rows are discovery pointers; they do not authorize work. Lookups also search
`tasks/archive/` in this workspace.

| Task | Purpose | Status | Next / waiting for | Review after | Updated |
| --- | --- | --- | --- | --- | --- |
```

Add one row per active or waiting task, using this shape; replace every placeholder before saving:

```markdown
| [<title>](tasks/<slug>.md) | <short purpose> | active | <next action> | <date or blank> | <updated date> |
```

Use workspace-relative paths, interpreted from the workspace root. Keep each cell brief; detailed context belongs in the task record. Leave Review after blank when absent. On meaningful changes to indexed fields, update the row as part of routine task maintenance. Do not retain completed or archived rows in another section of this index.
