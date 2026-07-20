# Cowork Skills & Agents

Give your AI assistant a team of 150+ specialists and a shelf of ready-made
workflows — so it handles more of your work, better, without you crafting a
single prompt.

## Get started (about 2 minutes)

Paste this to your AI assistant:

    Read INSTALL.md from https://github.com/shreeve1/Claude-Cowork/blob/main/INSTALL.md and follow its directions.

Your assistant outputs each skill as a `.skill` file in chat — click **Save
skill** in the Cowork desktop app to register it. New here? Run
`talk-it-through` next — it sharpens your plan and remembers what you decide.

Already installed? Paste the UPDATE.md line instead:

    Read UPDATE.md from https://github.com/shreeve1/Claude-Cowork/blob/main/UPDATE.md and follow its directions.

## What you get

- **150+ expert personas** — marketing, sales, finance, design, IT, and more.
  Describe a problem in plain English and the right specialist takes over.
- **Ready-made workflows** — planning, prototyping, memory, and a tool to build
  your own.

## Want a specialist right now?

Run `professional-guidance`, describe your problem in plain English, and it
becomes the best-fit expert from the library — no browsing, no restating.

## Want to build your own?

Run `workflow-builder` — it turns a workflow you have in mind into a reusable
skill, step by step.

## What's in the box

| Skill | What it does for you |
|---|---|
| `professional-guidance` | Describe a problem, get the right expert instantly. |
| `talk-it-through` | Start every conversation here — it sharpens your plan and remembers what you decide. |
| `prototype` | Mocks up a design or workflow so you can try it before you build it. |
| `workflow-builder` | Turns a workflow you have in mind into a reusable skill, step by step. |
| `personal-memory` | Remembers your preferences so you stop repeating yourself. |

---

<details>
<summary>Technical notes (how skills register)</summary>

Skills ship as self-contained `.skill` bundles committed under `.claude/cowork/`.
On install or update, your assistant outputs each new or changed bundle as a
`.skill` file in chat — click **Save skill** in the Cowork desktop app to
register it, and re-save after updates. Update only re-presents the skills that
changed.
</details>
