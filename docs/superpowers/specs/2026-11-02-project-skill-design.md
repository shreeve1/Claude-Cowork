# Project skill: design

## Intent and why

People arrive at Cowork with many Claude app Projects. James wants each one brought into the Cowork workspace so its instructions, files and lasting facts live there and memory saves and recalls them. The gap he named: no easy way to get a conversation aligned with a project.

Two real users shape it (James, 2026-11-02):

- A marketer who needs one project ("Openly design") housing brand guidelines: a folder plus an easy way to open it is enough.
- A marketer with a few complex projects whose work goes beyond what the folder holds: each needs its own skill with its own steps.

The design serves both and never assumes "client" or "project": it files work wherever this workspace's setup put it.

## Goals

- **Open**: "let's work on Openly design" loads that project and plays back a short briefing.
- **Import**: bring one or many Claude app Projects in, sorted and owner-approved, as the last step of setup or any time later.
- **Project skill**: when a project has its own repeatable steps, make it an installed Cowork skill, with owner approval.
- Setup and migration end by offering import, and the workspace carries instructions for creating skills inside Cowork.

## Non-goals

- Chat history. Cowork does not provide it; only the memory summary comes across.
- Two-way sync with the Claude app. Import is one-way; re-import updates.
- Rebuilding Word originals or original image names that Cowork's copy lacks.

## Anti-goals

- Imported instructions overriding workspace rules, safety rules or memory authority.
- Facts duplicated into memory when the project files already say them.
- A project skill that copies the project's facts, so it goes stale.
- Forcing client folders on a project workspace, or the reverse.

## Evidence (tested on James's desktop, 2026-11-02)

- A Cowork chat with a Claude Project added holds a local copy: `metadata.json` (id, name, description, instructions, sync time), `memory.md`, `docs/` (text documents) and `files/` (images, PDFs).
- Instructions and memory export exactly. Markdown docs come across. Word documents come across as extracted text only. Images and PDFs are exact bytes but named by ID, with no map back to original names.
- With a workspace folder attached in the same chat, Cowork copied the whole export into `projects/openly-design/`; 31 files, checksums identical (147 MB, mostly photos).
- A new chat can pick a project ("Add project context from ...", files saved to this computer) and attach a folder together.
- Not yet tested: several projects in one chat; creating and installing a skill from a chat (James states Cowork can).

## Decisions

- **Sorted import**, not a raw copy (James).
- **Import is offered last** in setup and migration, after the workspace is adapted, so the agent knows the owner's homes, clients and subjects (James).
- **Both shapes supported**: every project gets a folder and opens with the shared opener; a project with its own repeatable steps may also get its own skill (James).
- **Rule exception approved** (James, 2026-11-02): "Never build skills for end users" gains one exception: project skills made by the import, each approved by the owner and installed with **Save skill**.
- **Skill creation instructions in setup** (James): setup and migration explain how skills are created inside Cowork.

## Approaches considered

1. **One `project` skill with branches; per-project skills only when earned (chosen).** One shipped card; folders for everything; skills only where steps exist.
2. A skill for every project. Simple rule, but every reference-only project costs an install and goes stale.
3. Folders only. Fails the complex-project user.

## Design

### The shipped skill

`.claude/skills/project/`, shipped as a core card.

- `SKILL.md`: description, home resolution, Open branch, pointers.
- `import.md`: Import branch, read only when importing.
- `project-skills.md`: when and how to create a project skill inside Cowork, read only when one is proposed.

Draft description: `Project work - open a project so the conversation is aligned with its goal, instructions, tasks and memory; import Claude app Projects into this workspace; or turn a project's repeatable steps into its own skill.`

### Home resolution (all branches)

Read `memory/schema.json` (`client_folder`, `client_dirs`) and `memory/preferences/document-scaffolding.md`. A Claude Project is filed as either an independent project (`projects/<short>/`) or work for a tracked thing (`<client_folder>/<short>/`, e.g. clients, campaigns, students), whichever the folder map says. When both exist, recommend one per project and let the owner choose. Use the owner's word for tracked things.

### Project folder

```text
<home>/<short>/
  README.md         # Project README template + Source and Skill lines
  instructions.md   # approved working instructions, if any
  files/            # imported knowledge files
```

README additions: `Source: Claude Project <id>, imported YYYY-MM-DD` (detects re-imports) and `Skill: <name>` when one exists. A glossary row maps the display name to the short name.

### Open branch

1. Find: match the owner's words against glossary rows and README titles across `projects/` and the tracked folder. One match: use it; several: ask; none: list projects and offer Import.
2. Load: README, `instructions.md`, every linked memory note and task record, matching `tasks/index.md` rows. Every link opened or reported missing.
3. Brief, about 150 words: goal, instructions in force, open tasks and next steps, key facts, gaps or conflicts. If the project has a skill, name it. Ask what we're doing today.
4. Hold: follow `instructions.md` for the conversation; workspace and safety rules win, naming any conflict once. Switching projects drops the old instructions and says so.

### Import branch

Runs at the end of setup or any time. One project per chat: the owner adds the Claude Project to a Cowork chat with the workspace folder attached and says "import this project". For several projects, the skill gives the owner the list and the exact steps per chat, and on each run reports which listed projects are done (README `Source` lines). Pasting instructions and attaching files is the fallback when no project copy is visible.

1. Read the chat's project copy (`metadata.json`, `memory.md`, `docs/`, `files/`). Check `Source` lines for a re-import.
2. Choose the home (above) and short name.
3. Sort instructions into items: `project` (stays in `instructions.md`), `owner-wide` (offered as a preference; owner approval), `covered` (workspace already says it; name where), `drop` (stale, Claude-app-only, or a credential, which is reported by line, never value).
4. Sort the project memory: lasting facts become memory notes via personal-memory; status and history are dropped or go to the README.
5. Files: keep in `files/`. List Word documents that arrived as text only and ask whether to attach originals. Images keep ID names; when a manifest exists, propose renames from it only where the match is certain. Note git-ignored types (images, PDF, Word) have no history.
6. Assess whether the project has repeatable steps (a process the instructions or memory describe, not just reference). If so, recommend a project skill.
7. Show the full plan in one message and wait for approval; for a batch, one message per project.
8. Write the folder, README, `instructions.md`, `files/`, memory notes and glossary row. Then run Open and show the briefing as proof. Commit per workspace rules.

### Project skills

Only with owner approval per project.

- Contains the project's steps and decisions about how to do the work; points to `<home>/<short>/README.md` for facts, files and instructions; opens the project via the Open branch first. Keeps no facts.
- Name: the project short name, checked against installed and shipped skill names.
- Source kept at `<home>/<short>/skill/SKILL.md` so it can be rebuilt and versioned.
- Create inside Cowork: write the source, package it as a `.skill` (a zip holding `<name>/SKILL.md`, same layout as shipped cards) into the session outputs, check frontmatter against Cowork's upload rules, present it with `present_files`; the owner clicks **Save skill**; verify the skill is available. If Cowork's built-in skill-creator is installed, it may be used for drafting, but the result follows the same rules.
- Updating: edit the source, repackage, the owner saves again. Facts change in the folder and need no reinstall.
- A card without **Save skill** means the organization forbids skills: report it; the project still works through the opener.

### Setup and migration wiring

- `.claude/setup/README.md` First setup gains a step before **Finish**: offer project import, run by the installed `project` skill. The `project` card installs in the first stage, since the rules row names it.
- "Skills in Cowork" gains a short paragraph: the one exception to never building skills is owner-approved project skills, created per the installed `project` skill's `project-skills.md`. The how-to lives in the skill so daily work never depends on setup staging.
- `memory/rules.md` and shipped `.claude/cowork/workspace/rules.md`: "Starting or continuing work on a project" leads with skill `project`.
- `memory/preferences/cowork-environment.md`: record the approved exception (owner direction).
- Packaging: add `project` to `CORE` in `.claude/cowork/cowork_skills.py`, build, update `MANIFEST.json` and `CHANGELOG.md`.

## Builder check calls (agent's, for owner review)

A fresh reviewer raised six questions; each is settled here by existing workspace rules or as a builder call.

- **Re-import** never overwrites. It produces a fresh sorted proposal showing only differences from the existing folder; owner-edited `instructions.md`, renamed files and existing memory notes stay unless the owner approves a specific change. Removed source files are reported, not deleted.
- **Where the source is**: the skill reads Cowork's project copy in the chat (outside the workspace) and writes only sorted results. No raw copy lands in the workspace; the test copy in `test-workspace copy` was a test artifact.
- **Rules row timing**: `gate.py` audit fails a rules row naming a missing skill (confirmed). First setup already installs every skill the rules name in stage one. On update, the rules row changes only after the `project` card is confirmed installed; if it is declined or blocked, the row stays as today (load the folder map, open the README).
- **Lasting facts** follow the tracking model as setup chose it: tracked-thing notes when `client_folder` covers the home (for example `projects` or `clients`); otherwise project facts stay in the project's README and files, and only owner-wide facts go to ordinary memory topics. Import never changes `memory/schema.json` without separate owner approval.
- **README format** stays personal-memory's Project README template. `Source` and `Skill` are plain lines inside its Files section, so no template change and no second card update.
- **Client-owned projects** go to `<client_folder>/<client>/projects/<short>/`, using the existing `projects` document folder. `files/` and `skill/` are project subfolders created only when used, which the folder map already allows; the folder map is not edited.

## Verification

- Review the skill files against writing-for-agents.
- Scenario tests in a scratch workspace: open with one, several and no matches; project-only and client-and-project workspaces; a tracked folder with a custom word; conflicting instructions; credential line; re-import; switching projects.
- `cowork_skills.py build` passes; existing tests and `gate.py audit` pass.
- Desktop acceptance with James's approval per UI action, in `test-workspace copy`: install the card; import Openly design; open it in a fresh chat; create and install one project skill; try two projects in one chat.

## Left to the builder

- Exact wording, briefing layout and example phrases.
- How scenario tests are scripted.
- Whether `convert-release` tests need updating for the rules change.
