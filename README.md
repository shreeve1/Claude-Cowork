# Cowork Workspace

A ready-made agent workspace: instructions (`CLAUDE.md`), skills, memory and git hooks.
Your AI agent (Claude Cowork or Codex) installs it, updates it, migrates your existing
notes into it, and adapts it to how you work. You don't copy files by hand.

## Get started

1. Download this repo (**Code → Download ZIP**, unzip) or clone it.
2. Make a new, empty folder for your workspace.
3. Open your agent with access to this folder, the new folder, and (if you have one)
   your current agent setup.
4. Point your agent at the setup folder:

   > Read `<this folder>/.claude/setup/README.md` and follow `INSTALL.md` exactly.
   > Install into `<new folder>`. Migrate from `<my current setup>` (or "nothing to
   > migrate"). Ask me before anything is dropped.

The agent is done only when it has verified the result against the rules in `MIGRATING.md`.

## What the setup folder does

Everything is in [`.claude/setup/`](.claude/setup/README.md). Your agent picks the document:

| You want to | Agent follows |
|---|---|
| Install for the first time | `INSTALL.md`, then `MIGRATING.md` |
| Update to a newer version | `UPDATE.md` |
| Fit it to your app and way of working | `ADAPTING.md` |
| Go back to your old setup | `ROLLBACK.md` |
| See what a version contains | `MANIFEST.md` |
| Verify on a test system | `CHECKLIST.md` |

Your old setup is never edited. Nothing is dropped without your approval. When setup is finished, the agent deletes `.claude/setup/` from your new workspace (not from this repo); updates read it from the newer version.

## What you get

- **Memory** (`personal-memory`): remembers your preferences, rules and client facts so you stop repeating yourself.
- **100+ expert personas** (`professional-guidance`): describe a problem in plain English and the best-fit specialist takes over.
- **Thinking tools**: `talk-it-through` (stress-test a plan, record decisions), `brainstorm-idea`, `adhd` (parallel divergent ideation), `teach`.
- **Build your own** (`workflow-builder`, `startday-spec`): turn a workflow into a reusable skill, or build a start-of-day loop.
- **Writing and design quality** (`antislop` plus code, copy, UI, mobile and accessibility add-ons): filters out generic AI output.
- **Working tools**: `excalidraw-diagram`, `youtube` (transcript plus fact-check), `handoff` (continue work in a new session), `troubleshoot-my-pc`.
- **Upgrades** (`convert-release`): converts a new upstream release into this layout.
- **Safety**: local git history, with hooks that scan for secrets and refuse pushes that include private notes.

## Requirements

Claude Cowork or Codex. Git and Python 3.11+ are optional; setup works without them
and tells you what's off.

Some file browsers hide folders starting with a dot. The setup lives in `.claude/setup/`.
