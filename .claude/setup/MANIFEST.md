# MANIFEST.json

Every Release has `MANIFEST.json` at its root, and it stays in the workspace after setup. It lists every shipped file:

- `edition`: `friends` or `team`. `release`: the version number (higher is newer).
- For each file: its `class`, its `sha256` (taken with line endings turned into LF, so Windows CRLF copies still match) and its `mode`.

## What each class means

- `merge`: a shared file (`CLAUDE.md`, skills, hooks, these setup docs). Keep it as shipped. Personal content never goes into it. An update replaces it with the new version's copy.
- `seed`: a starter file the owner adapts (`CONTEXT.md`, `memory/glossary.md`, `memory/schema.json`, the folder map, `memory/rules.md`). Its content is the owner's. An update copies the owner's version across.
- `local`: a starting copy of a file that is the owner's from day one (`memory/index.md`, the generated indexes, `.gitignore`, `START-HERE.md`). Same rules as `seed`.

MANIFEST.json is a record of what shipped. Nothing checks it; an agent may use it to see which files the owner has changed.
