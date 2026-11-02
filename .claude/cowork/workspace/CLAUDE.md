# Claude Cowork workspace

This is an end-user workspace for Claude Cowork only, not the maintainer repository. Skills are installed in Cowork using ready-made `.skill` cards. Do not create or copy a shipped `.claude/skills/` source tree here. Preserve existing owner-created skills; installing or updating a skill still uses Cowork’s Save skill flow.

## Start each conversation

1. Read `memory/index.md`, `memory/glossary.md`, `memory/rules.md` and every Always-row file. Skip missing files. Before reading optional `tasks/index.md`, verify that it is a regular file inside this workspace with no escaping symlink; never create it on a startup read.
2. Load only relevant task records and linked memory. Index rows are pointers, not facts or permission. Match the work to its procedure or installed skill before acting.
3. Locate the actual installed personal-memory package for this session; verify its instructions, `tasks.md`, adjacent templates, `scaffold/` and helper scripts before relying on it. Never assume a maintainer path or a fixed `/home/...` path. Missing access or incomplete installation blocks the affected operation: report it and use the skill’s documented manual checks only where permitted.

## How to work

- Answer/status first, concise plain words. Expand unfamiliar acronyms and distinguish checked facts from guesses.
- Discussion is not approval to edit. Propose changes first unless the owner explicitly asks for that change. Ask before sends, publishing, deletions or live-system changes.
- Follow `memory/rules.md`; select one lead. Before running a saved procedure, check its required sections, real approval and verification with installed personal-memory’s `gate.py procedures`, or its manual readiness checks. Stop for missing requirements, approval points, failures or changed conditions. A stored procedure grants no current permission.
- Save documents in the folders in `memory/preferences/document-scaffolding.md`, not loose in the root. Open a project’s README before working on it. Preserve owner files and unrelated staged or uncommitted work.
- Use installed personal-memory’s `tasks.md` and adjacent templates for saved tasks. Lookups never start work; explicit pickup authorizes progress bookkeeping, not consequential actions. Completion needs the owner’s direction and archives the record before removing its active-index row. Nothing runs in the background merely because a task exists.

## Memory and recovery

At task end, check for corrections, preferences, settled decisions and useful lasting facts; capture qualifying items with installed personal-memory without asking. Do not store one-off details, unfinished status or credentials. Use `memory/README.md` and `memory/TEMPLATES.md`; memory authority and approval boundaries still apply. Before editing existing handwritten memory, use the installed skill’s verified recovery protocol; preserve previous bytes outside recall. Task/proposal recovery follows its `tasks.md`, not the memory-only helper. Failed preservation stops the edit.

Run installed personal-memory’s indexes/hubs helpers when needed and its memory audit from this workspace root. Resolve script paths from the installed package each session. If automated checks are unavailable, disclose permitted manual checks; never silently claim an audit passed. Report one line per saved item: `Memory saved: <path> - <summary>`, or `Memory check: nothing worth capturing.`

Exclude `.workspace-backups/` from routine search and recall. It holds retained update/recovery data, not current workspace instructions. Never prune it automatically.

## Git, when available

Git is optional. Commit only this session’s verified changes by exact path; preserve unrelated staged work. Never commit the owner’s existing staged documents to prepare an update. Never bypass enabled hooks. For the standalone memory-audit hook, verify the installed personal-memory helper folder and configure the machine-local `cowork.personalMemoryPath` setting using `git config --local cowork.personalMemoryPath "<verified installed personal-memory folder>"` and `git config core.hooksPath .githooks`. Recheck the installed folder after a session or machine change. A stale path blocks a memory commit until repaired. Push only with current approval.

## Updating

The owner downloads the ZIP, adds it to the conversation and pastes prompt 1, 2 or 3 from the Release README. Read setup instructions from the extracted ZIP, never from a copied maintainer skill source tree. Updates retain this workspace path, require a verified complete backup before writes, preserve owner content and stop for unresolved conflicts. Compare only projected user files, not all files in the maintainer Release. Install changed `.skill` cards from staging; retain only the package index for future comparisons. Do not delete a legacy `.claude/skills/` tree or owner skills automatically.
