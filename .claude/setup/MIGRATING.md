# Migrating the owner's content in

The goal: the workspace keeps exactly the shipped structure, and everything useful from the owner's old setup ends up inside it, in the right place. The old setup is read only: never edit, move or delete anything there.

The rules under "What must be true" at the end of this page must all hold. Setup is not done until you have verified each one.

## 0. Settle the tracking model first

Before moving anything, make sure "Tracking model" in `ADAPTING.md` is done: the owner's tracked things, their short names, subjects and hub rule. Old notes about a client, student, property or similar need those to exist before they can be filed.

## 1. Inventory: write the ledger first

Find everything in the old setup before moving anything. Look for:

- **Instructions files:** `CLAUDE.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`, `.github/copilot-instructions.md`, custom instructions pasted into an app's settings (ask the owner to paste them into a file you can read).
- **Memories and notes:** a `memory/` folder, a notes or Obsidian folder, an app's saved memories or project knowledge (the owner exports or copies them out).
- **Skills and prompts:** `.claude/skills/`, `.claude/skills/`, `.opencode/skills/`, `~/.codex/`, saved prompts.
- **Tool connections:** MCP entries in an app's config. List the server names only. Never copy tokens or passwords.

Create `memory/migration-ledger.md` in the workspace:

```markdown
# Migration ledger

Source: <full path of each old folder or file, one Source line each>

| Source | Destination | Outcome | Note |
|---|---|---|---|
| CLAUDE.md | memory/preferences/answer-style.md | moved | |
| memory/notes/ | memory/docs/old-notes.md | merged | three notes combined |
| .opencode/node_modules/ | | dropped | installed packages, not content; owner agreed |
```

- One row per file, or one row per folder when the whole folder goes to one place (end the Source with `/`). Source paths are relative to their `Source:` line.
- Outcome is exactly one of `moved`, `merged`, `dropped`, `none`.
- `moved` / `merged`: Destination is the path inside the workspace (several, comma-separated, if it was split).
- `dropped`: Note says why, and the owner agreed.
- Nothing to migrate: no `Source:` line and a single row with outcome `none`.

Setup fails if any file under a `Source:` path has no row.

## 2. Map each item to its destination

| What the owner has | Destination |
|---|---|
| A rule about how the agent should behave (tone, format, "always", "never") | A preference note in `memory/preferences/`, plus a row in `memory/rules.md` (use the `personal-memory` skill) |
| A fact about the owner, their tools, machine or setup | A doc note in `memory/docs/` |
| Lasting facts about a person or thing the owner tracks (client, student, property...) | A Client Memory note `memory/<client_folder>/<subject>/<short>/<slug>.md` (`clients` unless `memory/schema.json` sets `client_folder`), one fact per note, under the subjects agreed in "Tracking model" (`personal-memory` skill, then `hubs.py`). Not `memory/docs/`. |
| A repeatable process | A workflow note in `memory/workflows/<topic>/` (topics in `memory/schema.json`) |
| A decision settled earlier | A decision note in `memory/decisions/<topic>/` |
| Text style for email or messages | `memory/email/` or `memory/voice/` |
| A shorthand name (person, company, system) | A row in `memory/glossary.md` |
| A word the owner uses in a specific way | `CONTEXT.md` |
| Unsorted notes worth keeping | `memory/candidates/` |
| Raw material the owner wants kept as-is | `memory/raw/` (git-ignored) |
| Their own `memory/schema.json` (subjects, `client_folder`, topics) | Merged into the new `memory/schema.json`, never replaced blindly: keep the new file's topics and keys, add the owner's `client_subjects`, and keep their `client_folder`. Every subject an old note uses must be listed, or the audit fails. |
| A skill of their own (no shipped skill with that name) | `.claude/skills/<name>/`, copied whole |
| An old copy of a shipped skill | Not copied. The shipped skill wins. Any difference the owner relies on becomes a preference note naming the skill. |
| Documents, reports, research | The folder the folder map names (`memory/preferences/document-scaffolding.md`) |
| A whole instructions file | Split by the rows above. Lines that only repeat shipped `CLAUDE.md` rules are dropped, with the owner's OK. |

Never put personal content into a shipped file (`CLAUDE.md`, a shipped skill, `.claude/setup/`). Those are replaced on every update; memory is not.

## 3. Ask once per group

Group the ledger by destination: rules and preferences, facts, workflows and decisions, names and words, own skills, documents, dropped. For each group, show the owner the list in one message and ask one question: "OK to put these here?" Change what they object to, then move on.

Ask about a single item on its own only when it clashes with a shipped rule (for example the old instructions say "answer at length" and `CLAUDE.md` says "keep responses concise"). Show both, ask which wins, and record the answer as a preference note.

## 4. Move the content

Write each destination. After writing memory notes, if Python is present, run `python .claude/skills/personal-memory/indexes.py` and `python .claude/skills/personal-memory/hubs.py`, then add a row to `memory/index.md` for each new note under `memory/preferences/`, `docs/`, `email/`, `voice/` or `guides/`. Without Python, add those rows by hand.

Then remove anything in the workspace that is not shipped and not in the folder map: old config files, old folders, extra copies. The workspace root holds only shipped files, folders from the folder map, `.gitignore` and `.mcp.json`. A short pointer file such as `CLAUDE.md` containing only "Read CLAUDE.md" is allowed when the owner's app needs one.

## 5. Verify

Back to `INSTALL.md` step 7 (or `UPDATE.md`). Fix every failure. Never weaken the rules, the manifest or the ledger to pass.

## What must be true

- Every file in `MANIFEST.json` is present, except `.claude/setup/`, which `INSTALL.md` step 12 removes once setup is finished. Files marked `merge` are byte-for-byte as shipped (line endings aside). Files marked `seed` or `local` are the owner's to edit.
- Nothing from an old layout remains: `.opencode/`, `opencode.jsonc`.
- The workspace root holds only shipped files and folders, folders named in the folder map, `.gitignore`, `.mcp.json`, and a short pointer file if the app needs one.
- Every skill folder has a `SKILL.md`.
- `memory/migration-ledger.md` exists; every file under each `Source:` has a row; outcomes are valid; every destination exists, is not a shipped `merge` file and is not old layout; every `dropped` row has a reason.
- The workspace is not a clone (no remote, not the published Release repo).
- Git hooks are on: `.githooks` with Python 3.11+, `.githooks/nopython` without (push protection stays on either way).
- With Python: `python .claude/skills/personal-memory/gate.py --memory memory audit` passes.
