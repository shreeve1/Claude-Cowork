# Cowork Skills & Agents

A collection of reusable skills and specialist agents for your Cowork workspace, delivered as one-sentence prompts that any AI agent can follow.

## What's included

- **Skills** in `.claude/skills/` — structured workflows your AI agent can run (onboarding, interviews, memory management, prototyping, and more)
- **Agents** in `agents-library/` — 150+ specialist personas for design, engineering, marketing, sales, finance, and other roles

### Pointer skills

Each skill folder includes a `cowork/SKILL.md` — a lightweight pointer that tells Cowork where the real skill lives. During install or update, your AI agent will output these as `.SKILL` files in chat. When you see one, click **Save** in the Cowork desktop app to register it. Re-save them after any update so Cowork picks up the latest version.

## Getting started

Copy and paste this into your AI agent:

```
Read INSTALL.md from https://github.com/shreeve1/Claude-Cowork/blob/main/INSTALL.md and follow its directions.
```

**Already installed?** Use this instead:

```
Read UPDATE.md from https://github.com/shreeve1/Claude-Cowork/blob/main/UPDATE.md and follow its directions.
```

## Onboarding

First time installing? After the install prompt finishes, run the `cowork-onboarding` skill — it walks you through setting up your profile, memory, and connected tools.

## Professional guidance

Describe a problem in plain English and the `professional-guidance` skill matches you with the best-fit specialist from 100+ expert personas. It picks the right persona, confirms with you, then becomes that specialist in-session — no need to browse or restate anything.

## Building your own skills

Two paths depending on what you need:

**Have a clear workflow in mind?** Use the `workflow-builder` skill — it walks you through designing a reusable skill from scratch, step by step.

**Need something custom?** Run the agency intake loop (`agency-intake` → `agency-build` → `agency-feedback`). The intake interviews you and hands off a spec — then James builds it with you directly, ships it for testing, and iterates from your feedback.
