# Decision Memory Format

This replaces the old ADR step. Office and admin staff shouldn't be asked
whether to record a decision — when a session wraps up, decisions worth keeping
are written to personal memory automatically.

Decisions are **promoted memory**, written straight into `memory/decisions/`.
Everything still follows the conventions in
`memory/README.md` and `memory/TEMPLATES.md`.

## Where it goes

- One file per decision: `memory/decisions/<topic>/decision-<slug>.md`
- Create the `<topic>` folder lazily — only when the first decision in it is recorded. Pick the topic from the `topics` list in `memory/schema.json` (a new topic only with the owner's OK).
- If a later session changes an earlier decision, overwrite that decision's file in place (bump `updated`; one `Changed YYYY-MM-DD: <why>` line only if the reason still matters) rather than creating a duplicate.
- Before creating a new file, scan `memory/decisions/<topic>/` and `memory/decisions/index.md` for an existing matching decision.
- After writing, update the sub-index: run `python3 .claude/skills/personal-memory/indexes.py` (then `gate.py audit`). 15-file rule: a memory folder holding more than 15 `.md` files directly gets topic subfolders plus a generated index; `gate.py crowded` reports it.

## File template

```md
---
title: Short decision title
summary: One line shown on the decision index
type: decision
status: promoted
created: YYYY-MM-DD
updated: YYYY-MM-DD
topics: [decision]
---

## Decision

{1-3 sentences: what was decided and why. Plain language.}

## Notes

- Alternatives considered, or constraints behind it — only if worth remembering.
- Prefer role/process summaries over client names unless the client-specific constraint is essential.
```

Keep it short. The value is recording *that* a decision was made and *why* — not filling sections. Most decisions are a single paragraph.

## What qualifies as a decision worth recording

Record a decision when it would change what gets done and a future session
should not have to re-litigate it. Typically:

- **Process choices.** "Invoices go out on the 1st of the month, not at month-end."
- **Who-does-what.** "Sign-off is the Client's job; manager approval is internal and separate."
- **Tool or system choices that are awkward to change.** "We track all client requests in the ticket system, not email."
- **Scope and boundary calls.** "We don't chase payment under £50 — it carries to the next invoice."
- **Deliberate deviations from the obvious.** Anything where someone later would assume the opposite and try to "fix" it.
- **Constraints that aren't obvious from the work itself.** "Some clients require 48 hours' notice before onsite visits." Use client names only when the decision is inherently client-specific.

## What to skip

- Purely transient, one-off details with no future relevance.
- Anything that just restates a decision already recorded, without changing it.
- Secrets, credentials, or sensitive client/third-party specifics — summarize and redact per `memory/README.md`.
- Client names when a role, process, or category summary preserves the useful rule.

## After writing decisions

1. Add or update each decision file in `memory/decisions/<topic>/`.
2. Run `python3 .claude/skills/personal-memory/indexes.py` to regenerate the sub-index `memory/decisions/index.md` (decisions are listed there, not per-file in `memory/index.md`).
3. Run `python3 .claude/skills/personal-memory/gate.py --memory memory audit`, trim any file you touched this session that it warns about, then commit per "Commit at the end of every task" in `CLAUDE.md`. The commit message is the memory log.
4. Tell the user, in one line, which decisions were recorded and where.
