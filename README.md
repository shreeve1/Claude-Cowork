# Cowork Workspace

A ready-made agent workspace: instructions (`CLAUDE.md`), skills, memory and git hooks.
Your AI agent in Claude Cowork sets it up, updates it, brings your existing
notes into it, and adapts it to how you work. You don't copy files by hand.

## Start here

Choose the situation that matches you. Only first-time setup needs you to download this repo; for migration and updates, the agent gets the source from the public GitHub repo.

In Claude Cowork, give the agent access to the local folders your chosen prompt names. Replace the bracketed descriptions with your actual folder names or paths.

### 1. I’m starting fresh

Use this if you have no existing notes, memory, or agent setup to bring across. Download this repo (**Code → Download ZIP**, unzip) or clone it, and create a new, empty folder for your workspace. Give the agent access to both folders.

**Copy and paste:**

```text
Read [downloaded folder]/.claude/setup/README.md and follow “First setup”.

Set me up in [new empty workspace folder]. I have nothing to migrate.

Help me choose where my files and notes should go, adapt the workspace
to how I work, and walk me through installing the Cowork skills.
```

### 2. I have an existing setup to migrate

Use this if you already have notes, saved memory, instructions, or skills and want to move into this workspace’s layout. Create a new, empty destination folder.

**Copy and paste:**

```text
Read .claude/setup/README.md in https://github.com/shreeve1/Claude-Cowork
and follow “First setup”, using [existing setup folder] as the migration source.
Fetch the workspace files from that repo; I do not have a downloaded copy.

Set up my new workspace in [new empty workspace folder].

Review my existing setup and show me what you recommend bringing across,
where it belongs, and what would be left behind. Wait for my approval
before migrating content. Leave my existing setup untouched.

Finish adapting the workspace and walk me through installing the Cowork skills.
```

### 3. I already use this workspace and want to update

Use this if you already use this workspace and want the latest version in the same folder. Give the agent access to your current workspace; no download or new workspace folder is needed. The agent fetches the source and verifies a backup before making changes.

**Copy and paste:**

```text
Read .claude/setup/README.md in https://github.com/shreeve1/Claude-Cowork
and follow “A newer version arrived”, including “Older Releases” if needed.
Fetch the latest workspace files from that repo.

Update my existing workspace at [current workspace folder] in place.
Create and verify a backup before changing anything.

Preserve my notes, memory, rules, saved tasks, documents, and personal skills.
Show me any conflicts and ask before removing or replacing my own changes.

Show me what changed, walk me through any changed Cowork skill installs,
and verify the update. Keep using the same workspace folder.
```

### Not sure which applies?

Give the agent access to your existing setup and ask:

```text
Read .claude/setup/README.md in https://github.com/shreeve1/Claude-Cowork
and inspect my existing setup at [existing folder]. Tell me whether I need
a migration or an update, and explain why. Do not change anything yet.
```

In Claude Cowork, the agent shows a card for each skill to install: click **Save skill** on each. Video skills are optional. Keep your workspace folder attached when using its skills.

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

Migration leaves your old setup untouched. Updates change your existing workspace only after a verified backup, preserving your personal content. Nothing is dropped without your approval. When first setup or migration is finished, the agent deletes `.claude/setup/` from your new workspace (not from this repo); updates read the guide from GitHub.

## Projects or clients: fit the workspace to your work

Setup chooses the layout from the agent or bot's purpose. Non-client work uses `projects/<short>/README.md` with a goal, completion check, and links to files, saved tasks and memory. It chooses useful subfolders instead of inheriting client ticket folders. Client work can retain `clients/` and still have independent projects; other bots can use their own recurring subjects.

Procedure topics are chosen during setup. Empty workflow indexes are normal until a procedure has been verified and approved. These formats ship in the ready-made personal-memory and memory-setup packages; existing Cowork users must save the updated skill cards to update their installed copies. Source-folder edits alone do not update installed skills.

## What you get

- **Memory** (`personal-memory`, `memory-setup`): remembers preferences, rules, procedures and client facts. Checks saved procedures before use and preserves previous memory content before edits. `memory-setup` sets memory up in this or another project.
- **Saved tasks** (part of `personal-memory`): records unfinished work in this workspace, resumes it on request, and archives completed work. The compact active/waiting index loads at startup; task records are not permission to act, and nothing runs in the background.
- **Meetings** (`meeting`): processes transcripts from a folder, files lasting facts, drafts follow-ups for approval and archives the transcript.
- **100+ expert personas** (`professional-guidance`): describe a problem in plain English and the best-fit specialist takes over.
- **Thinking tools**: `talk-it-through` (stress-test a plan, record decisions), `brainstorm-idea`, `adhd` (parallel divergent ideation), `teach`.
- **Build your own** (`workflow-builder`, `startday-spec`): turn a workflow into a reusable skill, or build a calendar-aware start-of-day loop.
- **Writing and design quality** (`antislop` plus code, copy, UI, mobile and accessibility add-ons): filters out generic AI output.
- **Working tools**: `excalidraw-diagram`, `drawio` (diagrams you edit yourself in draw.io in your browser), `youtube` (transcript plus fact-check), `handoff` (continue work in a new session), `troubleshoot-my-pc`.
- **Video** (HyperFrames, from HeyGen, Apache-2.0): 20+ skills for making videos from a URL, PR, script or music: `hyperframes` is the entry point. Licence in `.claude/third-party/hyperframes/`.
- **Safety**: git history, with a commit hook that scans for secrets and checks memory.

## Working with your workspace

Use ordinary language; these are example phrases, not special commands. Keep the workspace attached in Cowork so the agent can read and update it.

### Procedures: a repeatable way to do something

A procedure is a tested, approved set of steps for the agent to follow when the same situation comes up again. A workflow is the broader process; a saved procedure makes its repeatable steps explicit.

To create one:

1. Describe the work and when the procedure should apply.
2. The agent checks for an existing procedure and proposes the steps, approval points, and how to check the result.
3. Run the steps together and verify they work. If the work cannot be tested yet, leave it as a draft rather than an approved procedure.
4. Review the full procedure and approve it before the agent saves it and connects it to the situations where it should be used.

Saved procedures live under `memory/workflows/`. The agent checks the matching procedure before using it, stops for required approvals, and stops if a step fails or the situation has changed. A saved procedure is not permission to send messages, delete data, or change a live system.

| You want to | Example phrase |
|---|---|
| Create a procedure | “Create a procedure for X. Help me work through it, test the steps, and show me the full procedure before saving it.” |
| Find an existing procedure | “Do we already have a procedure for X? Show me what it covers.” |
| Use a procedure | “Use our procedure for X. Stop at any approval points.” |
| Change a procedure | “Our procedure for X has changed. Propose an update, verify the changed steps with me, and wait for my approval before saving it.” |
| Draft a guide for someone to follow | “Write a step-by-step guide for X in this project’s documents, not an agent procedure.” |

### Tasks: unfinished work you can pick up later

A saved task holds the goal, useful context, progress, and the next action for a piece of work. It is not a reusable procedure. Task records live in `tasks/`; a short active/waiting list is in `tasks/index.md`, and closed records go to `tasks/archive/`.

The usual flow is: **save the task, pick it up, record progress or a blocker, then complete or archive it**. Once you ask the agent to continue a task, it keeps the progress and next action up to date at meaningful stopping points. You tell it when the task is complete.

| You want to | Example phrase |
|---|---|
| Save something for later | “Create a task for X. Save the goal, what we know, and the next action. Don’t start the work yet.” |
| Save where you stopped | “Save this as a task so we can pick it up later. Include what we tried and what still needs doing.” |
| Find a task without starting it | “Look up the task about X and tell me where we left it. Don’t resume it yet.” |
| Resume work | “Pick up the task about X and continue from the next action.” |
| Review open work | “What needs attention? Show me active tasks, anything waiting, and review dates that have arrived.” |
| Record a blocker | “Mark the task about X as waiting for Y. Record what needs to happen before we can continue.” |
| Finish a task | “The task about X is complete. Record the outcome and archive it.” |
| Stop unfinished work | “Archive the task about X without marking it complete. Record what we left unfinished and why.” |
| Reopen closed work | “Reopen the archived task about X so we can continue it.” |

Use the task’s title or ID if several tasks sound similar. Looking up or reviewing tasks does not start them. A waiting status or review date does not schedule a reminder or run anything in the background. Continuing a task does not grant permission for sends, publishing, deletions, or live-system changes.

### Other useful phrases

| You want to | Example phrase |
|---|---|
| Think before changing anything | “Help me talk through X. Recommend an approach, but don’t change files yet.” |
| Remember a preference | “Remember that I prefer X when we do Y.” |
| Check what is already known | “What do you remember about X? Check the saved notes before answering.” |
| Correct an outdated fact | “The saved note about X is out of date. It is now Y; update it and tell me what changed.” |
| Continue in another chat | “Create a handoff for a new chat with the goal, what we checked, and what to do next.” |

You do not have to ask the agent to remember every useful fact: it checks for lasting facts, preferences, and settled decisions at the end of a task. Saving memory is separate from approving a procedure or authorizing an action.
