# Cowork Skills & Agents

Give your AI assistant a team of 150+ specialists and a shelf of ready-made
workflows — so it handles more of your work, better, without you crafting a
single prompt.

## Get started (about 2 minutes)

Paste this to your AI assistant:

    Read INSTALL.md from https://github.com/shreeve1/Claude-Cowork/blob/main/INSTALL.md and follow its directions.

That's it. New here? Run `cowork-onboarding` next — it sets up your profile,
memory, and connected tools for you.

Already installed? Paste the UPDATE.md line instead:

    Read UPDATE.md from https://github.com/shreeve1/Claude-Cowork/blob/main/UPDATE.md and follow its directions.

## What you get

- **150+ expert personas** — marketing, sales, finance, design, IT, and more.
  Describe a problem in plain English and the right specialist takes over.
- **Ready-made workflows** — onboarding, interviews, memory, prototyping, and
  tools to build your own.

## Want a specialist right now?

Run `professional-guidance`, describe your problem in plain English, and it
becomes the best-fit expert from the library — no browsing, no restating.

## Want to build your own?

- **Have a workflow in mind?** Run `workflow-builder`.
- **Want something built for you?** Run `agency-intake` and James builds it with
  you, ships it to test, and refines it from your feedback.

## What's in the box

**Get set up**

| Skill | What it does for you |
|---|---|
| `cowork-onboarding` | Gets you running on day one — profile, memory, and connected tools. |

**Get expert help**

| Skill | What it does for you |
|---|---|
| `professional-guidance` | Describe a problem, get the right expert instantly. |
| `talk-it-through` | Start every conversation here — it sharpens your plan and remembers what you decide. |
| `interview` | Gets your idea out of your head with the right questions. |
| `prototype` | Mocks up a design or workflow so you can try it before you build it. |

**Build your own**

| Skill | What it does for you |
|---|---|
| `workflow-builder` | Turns a workflow you have in mind into a reusable skill, step by step. |
| `agency-intake` | Kicks off a custom skill built for you by James. |
| `agency-build` | Builds your custom skill from the intake. |
| `agency-feedback` | Sends your test notes back so James can refine the skill. |
| `project-to-skill` | Turns a Claude Project you already use into a reusable skill. |
| `skill-creator` | Helps you create a new skill from scratch. |
| `skill-scaffolder` | Sets up the files for a new skill so you start clean. |
| `cowork-pointer` | Lets you tweak a skill without reinstalling it. |
| `writing-great-skills` | The reference for writing skills that behave predictably. |

**Housekeeping**

| Skill | What it does for you |
|---|---|
| `personal-memory` | Remembers your preferences so you stop repeating yourself. |
| `handoff` | Hands your work to the next session without losing context. |

---

<details>
<summary>Technical notes (how skills register)</summary>

Each skill folder includes a `cowork/SKILL.md` pointer that tells Cowork where
the real skill lives. On install or update, your agent outputs these as `.SKILL`
files in chat — click **Save** in the Cowork desktop app to register each one,
and re-save after updates.
</details>
