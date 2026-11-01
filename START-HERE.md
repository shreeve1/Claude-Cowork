# Start here

This is a ready-made agent workspace: instructions (`CLAUDE.md`), skills, memory and git hooks. Your AI agent in Claude Cowork sets it up with you and moves your own notes and rules into it. You don't copy files by hand.

## What you need

- Claude Cowork on Windows.
- Nothing else is required. Git and Python 3.10+ add version history and the commit checks; the setup works without them and your agent tells you what is off.

Memory edits preserve verified previous content in `.memory-recovery/` even without Git. Without Python, the agent must copy and verify with file tools and disclose manual-only checks; if verification is unavailable, it stops. Recovery may contain sensitive summaries; it is ignored, not encrypted. Release copies exclude it; in-place updates keep recovery in place and include it in the verified pre-update backup. Migration copies recovery separately only with owner approval.

## Fit it to your agent or bot

Setup chooses the folder layout from the work you do. With no clients, independent work uses `projects/<short>/README.md` and useful project folders instead of client ticket folders. Client work can keep `clients/` and still have independent projects. Other bots can organize around the things they look after. Tell setup the bot's purpose; it personalizes memory subjects and procedure topics too.

A project groups related work; saved tasks track individual pieces of unfinished work. Verified, owner-approved agent procedures go in `memory/workflows/<topic>/`. An empty workflow index is normal until there is a real procedure to save.

## Saved tasks

Say “create a task”, “look up task X”, “continue task X”, “what needs attention?”, or “complete task X”. Tasks stay in this workspace; agents maintain progress after explicit pickup. Completion archives the record and removes its active-index row. Pending proposals stay separate and never prevent cleanup. Detailed formats ship with personal-memory; no external writing skill is required.

Task updates preserve previous content in `.task-recovery/` with or without Git. It is sensitive plaintext, excluded from release copies, retained through upgrades, and copied separately only with owner approval. File-only tools must verify preservation; unavailable safeguards block the affected operation rather than silently discard content.

## First setup

1. Make a new, empty folder for your workspace.
2. Open your agent with access to three folders: this one, the new empty one, and (if you have one) your current agent setup.
3. Paste this, with the paths filled in:

   > Read `<this folder>/.claude/setup/README.md` and set me up in `<new folder>`. Bring over what is useful from `<my current setup>` (or "nothing to migrate"). Decide where my files and notes go, and ask me before anything is dropped.

Your agent copies this workspace into the new folder, reads your old setup, decides where things belong and tells you what it did. Then it shows a card for each skill: click **Save skill** on each to install it. Video skills are optional.

Later, ask your agent "set up memory in `<folder>`" for any other project, or "bring my old notes from `<place>` into memory".

## Migrating an existing setup

No download is needed. Give the agent access to your existing setup and a new empty destination folder, then say:

> Read `.claude/setup/README.md` in `https://github.com/shreeve1/Claude-Cowork` and fetch the workspace files from that repo. Follow “First setup” to migrate from `<existing setup>` into `<new folder>`. Show me the placement plan and wait for approval before migrating content. Leave my existing setup untouched.

## A newer version arrived

No download or new workspace folder is needed. Give the agent access to your current workspace, then say:

> Read `.claude/setup/README.md` in `https://github.com/shreeve1/Claude-Cowork` and fetch the latest workspace files from that repo. Follow “A newer version arrived” to update `<current workspace>` in place. Create and verify a backup before changing anything. Preserve my personal content and ask before removing or replacing my own changes. Verify the update and walk me through changed Cowork skill installs. Keep using the same workspace folder.

## Upgrading from an earlier Release

Use the same update prompt, adding: “Include ‘Older Releases’, read everything that changed since my installed Release, and report any compatibility checks that need my help before applying the update.” The agent keeps the verified pre-update backup as the way back; restoring it requires your approval and preservation of work done since the update.

Some apps and file browsers hide folders whose names start with a dot; the setup instructions are in `.claude/setup/`.
