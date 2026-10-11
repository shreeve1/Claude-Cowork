# Promoted Memory Format (non-decision types)

This is the companion to [DECISIONS-FORMAT.md](./DECISIONS-FORMAT.md). It covers
the other types a `talk-it-through` session may settle and promote directly at
wrap-up: **preferences**, **workflows**, and **docs**.

Like decisions, these are **promoted memory** when settled in-session — the
user was actively in the loop, so the session itself is the approval and they
are promoted directly. Everything still follows the conventions in
`memory/README.md` and `memory/TEMPLATES.md`. Use this doc for routing and
shape; use `memory/TEMPLATES.md` for the canonical templates.

## Choosing the type

Pick by what the item *is*. When ambiguous, default to **decision** (see
DECISIONS-FORMAT.md).

- **preference** — how the user wants the assistant to behave or communicate.
  "Keep email replies to three sentences." "Don't use emojis."
- **workflow** — a repeated habit or sequence of steps the user follows.
  "Run the memory check before reporting a task complete."
- **doc** — an important reference, link, or path worth remembering, plus when
  to consult it. "The onboarding runbook lives at <path>; check it before
  provisioning a new user."

## Where it goes

These are **merge targets**, not one-file-per-item like decisions. Add to the
relevant section of the owning topic file rather than creating a new file per
item:

- **preference** → the closest existing file in `memory/preferences/` (email tone
  lives in `memory/email/`). A new file also gets a row in `memory/rules.md`.
- **workflow** → `memory/workflows/<topic>/` (e.g. `memory/workflows/memory/session-end.md`; create a new `memory/workflows/<topic>/<slug>.md` only if no existing file fits). Never write `type: procedure` files here: they are written only through an owner-approved change, never auto-captured.
- **doc** → the matching `memory/docs/<slug>.md`, one file per subject (create one only if none fits).

Before writing, scan `memory/index.md` and the target folder for an existing
matching entry. If one exists, overwrite it in place (bump `updated`) rather
than duplicating.

Workflows live in a topic folder picked from the `topics` list in
`memory/schema.json` (a new topic only with the owner's OK). After writing, run
`python3 .claude/skills/personal-memory/indexes.py` and `gate.py audit`.
15-file rule: a memory folder holding more than 15 `.md` files directly gets
topic subfolders plus a generated index; `gate.py crowded` reports it.

## File shape

Follow the **Promoted Topic File** template in `memory/TEMPLATES.md`:

```md
---
title: Topic Title
summary: One line shown on the index
type: preference | workflow | doc
status: promoted
created: YYYY-MM-DD
updated: YYYY-MM-DD
topics: []
---

## Active memory

- Durable rule, habit, or reference. One line each.

## Notes

- Last reviewed: YYYY-MM-DD
- Changed YYYY-MM-DD: why, only when the reason still matters.
```

When merging into an existing topic file, add a bullet under `## Active memory`,
bump `updated`, and note the change under `## Notes` — do not rewrite unrelated
rules. For **docs**, the `## Active memory` bullet should capture both the
reference and *when to consult it*.

## What qualifies

Promote a non-decision item when it was clearly settled in-session and a future
session should rely on it without re-asking. Typically:

- **preference:** a stated communication or behavior rule the user confirmed.
- **workflow:** a repeated sequence or habit the user wants followed by default.
- **doc:** a reference the user pointed to as durably important.
- **inferred, not explicitly confirmed:** write it automatically per the CLAUDE.md capture rule, but mark it `unverified` in Notes. Do not ask. There are no candidates.

## What to skip

- Purely transient, one-off details with no future relevance.
- Anything that just restates a promoted entry already recorded, unchanged.
- Passwords, secrets, or other credentials — omit automatically and never ask.
- Ticket Guides — never write them here; they are saved only through an owner-approved change (one `ticket-guide` approval) and stay redacted. Other client and third-party details (names, environments, contacts, config facts) are allowed.

## After writing

1. Add or update the entry in its topic file.
2. Add or update the row in the Promoted Memory table in `memory/index.md` (workflows appear via the generated sub-index `memory/workflows/index.md` — run `python3 .claude/skills/personal-memory/indexes.py` after writing).
3. Run `python3 .claude/skills/personal-memory/gate.py --memory memory audit`, trim any file you touched this session that it warns about, then commit per "Commit at the end of every task" in `CLAUDE.md`. The commit message is the memory log.
4. Tell the user, in one line, which items were recorded, their type, and where.
