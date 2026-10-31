# Start here

This is a ready-made agent workspace: instructions (`CLAUDE.md`), skills, memory and git hooks. Your AI agent in Claude Cowork sets it up with you and moves your own notes and rules into it. You don't copy files by hand.

## What you need

- Claude Cowork on Windows.
- Nothing else is required. Git and Python 3.10+ add version history and the commit checks; the setup works without them and your agent tells you what is off.

Memory edits preserve verified previous content in `.memory-recovery/` even without Git. Without Python, the agent must copy and verify with file tools and disclose manual-only checks; if verification is unavailable, it stops. Recovery may contain sensitive summaries; it is ignored, not encrypted. Release copies exclude it; upgrades retain the old workspace and copy recovery separately only with owner approval.

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

## A newer version arrived

Open your agent with the new version, a new empty folder, and your current workspace, then say: "Follow the 'A newer version arrived' section of `.claude/setup/README.md` in the new version." Your current workspace is left untouched; it is the way back.

## Upgrading from an earlier Release

Use this when your workspace was set up from an earlier Release, whichever one, and you want this version with your own content brought across. Open your agent with three folders: this one, a new empty folder, and your current workspace. Paste this, with the paths filled in:

> Upgrade my workspace at `<current workspace>` to the Release in `<this folder>`, building it in `<new folder>`. Follow `<this folder>/.claude/setup/README.md`, section "A newer version arrived", including "Older Releases". Read my current workspace's `CHANGELOG.md` (or `MANIFEST.json`) to see which Release I am on, and read this folder's `CHANGELOG.md` for everything that changed since. Bring all my notes, rules, procedures, decisions and my own skills across, in the places this Release uses. If I or my agent edited shipped files, show me those changes and ask before keeping or dropping each one. Change nothing in my current workspace. At the end, run the memory check and tell me what moved, what was left behind and why.

Your current workspace stays as it is; if anything looks wrong afterwards, keep using it.

Some apps and file browsers hide folders whose names start with a dot; the setup instructions are in `.claude/setup/`.
