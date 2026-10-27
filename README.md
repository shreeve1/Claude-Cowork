# Cowork Workspace

A ready-made agent workspace: instructions (`CLAUDE.md`), skills, memory and git hooks.
Your AI agent (Claude Cowork or Claude Code) sets it up, updates it, brings your existing
notes into it, and adapts it to how you work. You don't copy files by hand.

## Get started

1. Download this repo (**Code → Download ZIP**, unzip) or clone it.
2. Make a new, empty folder for your workspace.
3. Open your agent with access to this folder, the new folder, and (if you have one)
   your current agent setup.
4. Point your agent at the setup folder:

   > Read `<this folder>/.claude/setup/README.md` and set me up in `<new folder>`.
   > Bring over what is useful from `<my current setup>` (or "nothing to migrate").
   > Decide where my files and notes go, and ask me before anything is dropped.

Your agent copies the workspace, reads your old setup, asks you how you work, decides where things belong and tells you what it did. In Claude Cowork it then shows a card for each skill: click **Save skill** on each to install it. Video skills are optional.

## What the setup folder does

Everything is in [`.claude/setup/`](.claude/setup/README.md). `README.md` there is the one setup guide:

| You want to | Agent follows |
|---|---|
| Set up for the first time | `README.md`, "First setup" |
| Update to a newer version | `README.md`, "A newer version arrived" (and "Older Releases" if you skipped some) |
| Go back to your old setup | `README.md`, "Going back" |
| Fit it to your app and way of working | `ADAPTING.md` |
| Run the weekly memory sweep | `WEEKLY-SWEEP.md` |
| See what a version contains | `MANIFEST.md` |

Your old setup is never edited. Nothing is dropped without your approval. When setup is finished, the agent deletes `.claude/setup/` from your new workspace (not from this repo); updates read it from the newer version.

## What you get

- **Memory** (`personal-memory`, `memory-setup`): remembers your preferences, rules, procedures and client facts so you stop repeating yourself. `memory-setup` sets memory up in this or any other project.
- **Meetings** (`meeting`): processes transcripts from a folder, files lasting facts, drafts follow-ups for approval and archives the transcript.
- **100+ expert personas** (`professional-guidance`): describe a problem in plain English and the best-fit specialist takes over.
- **Thinking tools**: `talk-it-through` (stress-test a plan, record decisions), `brainstorm-idea`, `adhd` (parallel divergent ideation), `teach`.
- **Build your own** (`workflow-builder`, `startday-spec`): turn a workflow into a reusable skill, or build a calendar-aware start-of-day loop.
- **Writing and design quality** (`antislop` plus code, copy, UI, mobile and accessibility add-ons): filters out generic AI output.
- **Working tools**: `excalidraw-diagram`, `drawio` (diagrams you edit yourself in draw.io in your browser), `youtube` (transcript plus fact-check), `handoff` (continue work in a new session), `troubleshoot-my-pc`.
- **Video** (HyperFrames, from HeyGen, Apache-2.0): 20+ skills for making videos from a URL, PR, script or music: `hyperframes` is the entry point. Licence in `.claude/third-party/hyperframes/`.
- **Upgrades** (`convert-release`): converts a new upstream release into this layout.
- **Safety**: git history, with a commit hook that scans for secrets and checks memory.

## Requirements

Claude Cowork or Claude Code. Git and Python 3.11+ are optional; setup works without them
and your agent tells you what's off.

Some file browsers hide folders starting with a dot. The setup lives in `.claude/setup/`.
