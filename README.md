# Cowork Skills & Agents

A collection of reusable skills and specialist agents for your Cowork workspace, delivered as one-sentence prompts that any AI agent can follow.

## What's included

- **Skills** in `.claude/skills/` — structured workflows your AI agent can run (onboarding, interviews, memory management, prototyping, and more)
- **Agents** in `agents-library/` — 150+ specialist personas for design, engineering, marketing, sales, finance, and other roles

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

After install, run the `cowork-onboarding` skill — it walks you through setting up your profile, memory, and connected tools.

## Building your own skills

Two paths depending on what you need:

**Have a clear workflow in mind?** Use the `workflow-builder` skill — it walks you through designing a reusable skill from scratch, step by step.

**Need something custom?** Run the agency intake loop (`agency-intake` → `agency-build` → `agency-feedback`). The intake interviews you and hands off a spec — then James builds it with you directly, ships it for testing, and iterates from your feedback.
