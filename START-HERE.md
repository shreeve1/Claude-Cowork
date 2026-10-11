# Start here

This is a ready-made agent workspace: instructions (`CLAUDE.md`), skills, memory and git hooks. Your AI agent (Claude Cowork or Codex) sets it up with you and moves your own notes and rules into it. You don't copy files by hand.

## What you need

- Claude Cowork or Codex.
- Nothing else is required. Git and Python 3.11+ add version history and the commit checks; the setup works without them and tells you what is off.

## First setup

1. Make a new, empty folder for your workspace.
2. Open your agent with access to three folders: this one, the new empty one, and (if you have one) your current agent setup.
3. Paste this, with the paths filled in:

   > Read `<this folder>/.claude/setup/README.md` and follow `INSTALL.md` exactly. Install into `<new folder>`. Migrate from `<my current setup>` (or "nothing to migrate"). Ask me before anything is dropped.

Your agent copies this workspace into the new folder, moves your content in, and runs the check. It is not done until the check passes.

## A newer version arrived

Open your agent with the new version, a new empty folder, and your current workspace, then say: "Follow `.claude/setup/UPDATE.md` in the new version." Your current workspace is left untouched until the new one passes the check.

Some apps and file browsers hide folders whose names start with a dot; the setup instructions are in `.claude/setup/`.
