# Agents Library

All **187 agents** from The Agency, in Claude subagent format, organized by
division. Nothing here auto-loads — agents are invoked on demand, which keeps
the library effectively unlimited and avoids any subagent registration limits.

This is the single source of truth for agents in this workspace.
Agents are materialized into a produced skill's own `agents/` folder on demand.

## Layout

```
agents-library/
├── academic/            5 agents
├── design/              9 agents
├── engineering/        33 agents
├── finance/             5 agents
├── marketing/          24 agents
├── paid-media/          7 agents
├── product/             5 agents
├── project-management/  7 agents
├── sales/               9 agents
├── security/           10 agents
├── spatial-computing/   6 agents
├── specialized/        53 agents
├── support/             6 agents
├── testing/             8 agents
├── index.json         ← machine-readable catalog (187 entries)
└── README.md          ← this file
```

**Total: 187 agents across 14 divisions.**

Each `.md` file is a ready-to-use Claude subagent:

```yaml
---
name: <Agent Name>
description: <one-line specialty>
color: '#RRGGBB'
---
<body: identity, mission, workflows, deliverables, metrics>
```

## Picking agents (for skills / automation)

`index.json` is the catalog. Each entry:

```json
{
  "division": "engineering",
  "slug": "frontend-developer",
  "name": "Frontend Developer",
  "description": "Expert frontend developer specializing in ...",
  "color": "#3B82F6",
  "file": ".claude/skills/workflow-builder/agents-library/engineering/frontend-developer.md"
}
```

Filter by `division`, match on `name`/`description` keywords, then point at
`file`. A picker skill can read `index.json`, narrow candidates, and load the
chosen file's contents — no install or cap involved.

## How to invoke an agent

**On demand (recommended for this setup):** read the `.md` and adopt the
persona for the task. For example: *"Read `.claude/skills/workflow-builder/agents-library/engineering/sre.md`
and act as that agent."* This is what the picker skills will automate.

## Editing agents

These files **are** the source of truth — edit any `.md` directly. Each is plain
Claude subagent format (YAML frontmatter + Markdown body), no build step.

When you edit a file, keep the frontmatter fields in sync so `index.json` and the
file agree. If you change an agent's `name`/`description`/`color`, also update
the matching entry in `index.json` (same `slug`/`file`).

To **add** a new agent: drop a new `.md` into the right division folder (same
frontmatter shape), then add an entry to `index.json` with its `division`,
`slug` (filename without `.md`), `name`, `description`, `color`, and
`file` path.
