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

A shared procedure at `memory/workflows/<topic>/<slug>.md` contains only owner-approved, actually verified steps. Record real approval and verification dates, never dates invented to pass lint. Keep it within 6144 bytes and its summary within 160 characters; link optional troubleshooting separately.

```markdown
---
title: Verb Phrase - What It Does
summary: Trigger to outcome in at most 160 characters
type: procedure
status: promoted
created: YYYY-MM-DD
updated: YYYY-MM-DD
topics: [<topic>]
risk: read-only
approved: YYYY-MM-DD
verified: YYYY-MM-DD
---

## Active memory

Trigger: what starts this procedure.

### Prerequisites

Tools, inputs and access that must already be available.

### Steps

1. One verified action, with its exact command or click.

### Verify

Observable evidence that the intended result was reached.

## Related

None.

## Notes

Defined and tested with the owner; record the source of verification.
```

Use exactly `risk: read-only` or `risk: changes-state`. Changes-state procedures also require nonempty `### Approval` (the current-conversation ready check before action) and `### Recovery` (rollback, or explicit irreversibility and safe escalation), within Active memory. `approved` and `verified` are valid YYYY-MM-DD dates, not future dates. All shown sections and Trigger are required; Steps needs a numbered action. Fenced examples and empty sections do not count. Extra metadata and troubleshooting sections are allowed. `gate.py procedures` and `gate.py audit` check structure only, not truth, actual approval or permission to act.


## Changes-state Procedure File

Use this shape when a verified procedure changes state. Fill with real owner-approved steps and actual approval/verification dates; this unfilled template is not an executable or promoted procedure. Approval is a current-run stop, not a claim that saved metadata grants permission.

```markdown
---
title: Verified State-changing Workflow
summary: Trigger and intended change in at most 160 characters
type: procedure
status: promoted
created: YYYY-MM-DD
updated: YYYY-MM-DD
topics: [<topic>]
risk: changes-state
approved: YYYY-MM-DD
verified: YYYY-MM-DD
---

## Active memory

Trigger: the owner requests this specific state-changing workflow.

### Prerequisites

Describe the verified tools, access, inputs and original state needed.

### Approval

Show the exact proposed change and target; obtain permission in this conversation before the state-changing step. Stop if permission or prerequisites are missing.

### Steps

1. Inspect the target and capture its relevant current state.
2. After the Approval check, perform the owner-authorized verified change.
3. Stop on failure or changed conditions rather than improvising another change.

### Verify

Describe the observed evidence that confirms the intended outcome and detects unintended changes.

### Recovery

Describe the verified rollback and when to stop for approval; if irreversible, name the irreversible effect and safe escalation instead of promising undo.

## Related

None.

## Notes

Record real verification evidence and approval source; never invent dates to pass checking.
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
