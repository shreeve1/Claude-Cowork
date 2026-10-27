# Memory Templates

Markdown with small YAML frontmatter. A note is at most 6144 bytes and its `summary` at most 160 characters. Files state only what is true now.

## Promoted Topic File

For `preferences/`, `docs/` and `workflows/<topic>/`.

```markdown
---
title: Topic Title
summary: One line shown on the index, at most 160 characters
type: preference | doc | workflow | procedure | context
status: promoted
created: YYYY-MM-DD
updated: YYYY-MM-DD
topics: []
---

## Active memory

- Durable fact, rule or step.

## Related

- [Related topic](memory/docs/other-topic.md) - how it relates.

## Notes

- Changed YYYY-MM-DD: why, only when the reason still matters.
```

## Decision Memory File

Path: `memory/decisions/<topic>/decision-<slug>.md`.

```markdown
---
title: Short Decision Title
summary: One line shown on the index, at most 160 characters
type: decision
status: promoted
created: YYYY-MM-DD
updated: YYYY-MM-DD
topics: [<topic>]
---

## Decision

What was decided and why, in a few sentences.

## Notes

- Changed YYYY-MM-DD: why, only when the reason still matters.
```

## Procedure File

A Shared Procedure in `memory/workflows/<topic>/<slug>.md`, saved only with the owner's approval and made only of steps that were run and verified. `type: procedure` marks it: no agent writes or changes it without the owner's approval. Show the owner the full file and save only after a clear yes. Trigger, Steps, Related and Notes are required; add an optional section only when the procedure needs it. Over the 6144-byte limit: move failures and tuning into a sibling `<slug>-troubleshooting.md` and link it, rather than cutting steps.

```markdown
---
title: Verb Phrase - What It Does
summary: Trigger to outcome in one line, at most 160 characters
type: procedure
status: promoted
created: YYYY-MM-DD
updated: YYYY-MM-DD
topics: [<topic>]
---

## Active memory

Trigger: what the owner says or what happens that starts this procedure.

### Where everything is (optional)

- Tools, hosts, file paths and where credentials live (never the credentials).

### Defaults (optional)

- Values the owner set once and should not be asked again.

### Steps

1. **Short name.** One action, with the exact command or click.
2. **Ready check (hard stop).** The question to ask; continue only after the owner says yes in this conversation.

### When something goes wrong (optional)

- Known failures and fixes, or a link to `<slug>-troubleshooting.md`.

### Do not (optional)

- Actions that are never allowed while running this procedure.

## Related

- [Other procedure or note](memory/workflows/<topic>/other.md) - how it relates.

## Notes

- Last reviewed: YYYY-MM-DD
- Defined YYYY-MM-DD with the owner; verified by a real run on YYYY-MM-DD.
```

## Client Memory Note

Path: `memory/<client_folder>/<subject>/<short>/<slug>.md`. One fact per note. All six keys required; `gate.py audit` checks them.

```markdown
---
type: client-memory
client: <short>
subject: <subject from schema.json>
title: One-line fact
verified: YYYY-MM-DD
source: "the owner said"   # or a file path, ticket or session
---
One fact in one to three sentences. Link related notes by path.
```

## Index

Workflows and decisions are listed in their generated sub-indexes (`indexes.py`); `index.md` carries one row for each sub-index, plus one row per other note.

```markdown
| Page | Type | Summary | Updated |
|------|------|---------|---------|
| [Title](memory/docs/slug.md) | doc | summary | YYYY-MM-DD |
```

## glossary.md

One row per entity, grouped under the sections that have content. Thin rows: short form, expansion, a few words of identity.

```markdown
## Systems
| Shorthand | Identity |
| --- | --- |
| mon1 | Monitoring server |
```

## rules.md

One row per trigger; pointers only. Skills as skill `name`, paths backticked and project-relative.

```markdown
| When | Lead | Also load | Note |
|---|---|---|---|
| Changing the alert rules | | `memory/workflows/monitoring/alert-rules.md` | |
```
