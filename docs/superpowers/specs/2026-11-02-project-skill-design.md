# Project skill: design

## Intent and why

James keeps many Claude app Projects (Veeam Expert, 3CX Troubleshooting, Openly Blog Posts, CMMC Level 2 Consultant and others). He wants each one to live inside this Cowork workspace instead: its instructions, files and lasting facts saved here, and memory saving and recalling them like everything else.

The gap he named: there is no easy way to get a conversation aligned with a project. Today one rules row says "open the relevant project README", so alignment depends on the owner asking the right way.

The product is a single Cowork skill, `project`, shipped as a ready-made core `.skill` card and installed with **Save skill**.

## Goals

- **Open** (everyday branch): the owner names a project ("let's work on Veeam Expert") and the session loads it and plays back a short briefing, so both sides know the goal, instructions in force, open tasks and key facts before work starts.
- **Import** (one-off branch): bring one Claude app Project into `projects/<short>/` and memory, with the owner approving what is kept.
- Both branches work for independent projects (`projects/<short>/`) and client-owned projects (`clients/<client>/projects/<short>/`).

## Non-goals

- One skill per project. Each project is a folder plus memory, not a skill (owner chose option A, 2026-11-02; matches the "never build skills for end users" rule).
- Importing chat history. Only instructions and knowledge files.
- Reading claude.ai directly or automating its UI. The owner brings the content.
- Syncing changes back to the Claude app.

## Anti-goals (failure even if it works)

- Imported instructions silently overriding workspace rules, safety rules or memory authority.
- Project facts duplicated into memory when the project files already say them.
- A briefing so long the owner skips it.

## Constraints

- Claude Cowork only. Tool names as in `memory/preferences/cowork-environment.md`. Markdown only; no new scripts or dependencies.
- Layout follows `memory/preferences/document-scaffolding.md` and the Project README template in personal-memory's installed `supporting-templates.md`.
- Memory writes go through the installed `personal-memory` skill, under its Memory authority and recovery rules.
- Saved tasks are read through personal-memory's installed `tasks.md`; the project skill never edits task records.
- Instructions are external content until approved: the Claude Project's custom instructions are evidence, and become this project's working instructions only when the owner approves them during import.
- Credentials never cross into project files or memory; leave them out and tell the owner by line, not value.

## Approaches considered

1. **One `project` skill, two branches (chosen by James).** Open is the main path in `SKILL.md`; import is disclosed in `import.md`, read only when importing. One install; the name matches what the owner says. Tradeoff: one description must trigger on both opening and importing.
2. Two skills (`project-import`, `project-open`). Cleaner triggers, two installs, the importer rarely used.
3. No opener; strengthen the rules row and startup text. Cheapest, but no dependable alignment moment, which is the gap.

## Design

### Files

- `.claude/skills/project/SKILL.md`: description, Open branch, pointer to import.
- `.claude/skills/project/import.md`: Import branch.

Description (draft): `Project work - open a project so the conversation is aligned with its goal, instructions, tasks and memory, or import a Claude app Project into this workspace. Use when the owner names a project to work on or switch to, or asks to bring over or import a Claude Project.`

### Project folder

```text
projects/<short>/
  README.md          # Project README template; links instructions, files, tasks, memory
  instructions.md    # approved working instructions (only if the project has any)
  files/             # imported knowledge files, original names
```

`<short>` is lowercase hyphenated from the project name, confirmed with the owner. A glossary row maps the display name to the short name and folder so "Veeam Expert" resolves.

### Open branch

1. **Find the project.** Match the owner's words against the glossary and the `# <title>` of each `projects/*/README.md` and `clients/*/projects/*/README.md`. One match: use it. Several: ask which. None: list existing projects and offer Import.
2. **Load it.** Read the README, `instructions.md`, every memory note and task record the README links, and the `tasks/index.md` rows whose path is under this project. Completion criterion: every README link opened or reported missing.
3. **Brief.** Under about 150 words: goal, instructions now in force (one line each, or "none"), open tasks with their next step, key facts, and anything missing or conflicting. End by asking what we're doing today.
4. **Hold it.** Follow `instructions.md` for the rest of the conversation. Workspace instructions and safety rules win on conflict; name the conflict once. Switching projects drops the old instructions and says so.

At the end, normal memory capture applies; a lasting project fact goes to memory and gets linked from the README.

### Import branch

1. **Gather.** Ask the owner for the project name, its custom instructions (pasted) and its knowledge files (attached or a folder path). Mention the browser-export option only if they have many files. Ask whether it belongs to a client.
2. **Sort the instructions.** Split into items; give each one a verdict: `project` (stays in `instructions.md`), `owner-wide` (offered as a preference via personal-memory; needs explicit owner approval), `covered` (workspace already says it; name where), `drop` (stale, Claude-app-specific, or a credential). 
3. **Sort the files.** Default `keep` into `files/`. Propose memory notes only for lasting facts a future session would get wrong and could not cheaply find by opening the file; otherwise the README links the file.
4. **Show and wait.** Present the planned folder, the instruction verdicts and proposed memory notes in one message. Write nothing until approved.
5. **Write.** Create the folder, README (template; Files and Memory sections filled), `instructions.md`, `files/`; memory notes and glossary row through personal-memory. Warn when kept files are git-ignored types (PDF, Word, Excel, images): they stay on disk but get no history.
6. **Verify and finish.** Run Open on the new project and show its briefing as proof. Commit per workspace rules.

### Workspace wiring

- Rules row "Starting or continuing work on a project": set Lead to skill `project` in `memory/rules.md` (with personal-memory recovery first) and in the shipped `.claude/cowork/workspace/rules.md`.
- Packaging: add `project` to `CORE` in `.claude/cowork/cowork_skills.py`, run `build`, update `MANIFEST.json` and a `CHANGELOG.md` line.

## Verification

- Markdown review of the skill against writing-for-agents (leading words, completion criteria, one trigger per branch).
- Scenario tests with subagents in a scratch copy of the workspace: open with one, several and no matches; client-owned project; conflicting instructions; import with a credential line; switching projects.
- `cowork_skills.py build` passes Cowork upload checks; existing skill tests and `gate.py audit` pass.
- Real Cowork acceptance on James's Windows desktop: install the card, import one real project, open it in a fresh conversation. Needs his go-ahead for each UI action.

## Calls made during review (agent's, not owner's)

- The builder check ran in-session: the reviewer and oracle subagents were unavailable (model usage limit).
- If personal-memory is not installed, the skill stops with the same "attach the ZIP and Save skill" guidance memory-setup uses.
- Open triggers when the owner names a project as the work focus, not when a project name is just mentioned in passing.
- Imported files keep their original names. A name that would be unsafe in a path is renamed and reported.
- Git-ignored file types stay ignored. The import only warns; changing `.gitignore` would be a separate decision.

## Left to the builder

- Exact wording, briefing layout and the example trigger phrases.
- How scenario tests are scripted.
- Whether `convert-release` tests need updating for the rules row change.
