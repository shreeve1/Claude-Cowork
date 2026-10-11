# MANIFEST.json

Every Release has `MANIFEST.json` at its root, and it stays in the workspace after setup. It lists every shipped file:

- `edition`: `friends` or `team`. `release`: the version number (higher is newer).
- For each file: its `class`, its `sha256` (taken with line endings turned into LF, so Windows CRLF copies still match) and its `mode`.

## What each class means

- `merge`: a shared file (`CLAUDE.md`, skills, hooks, these setup docs). It must stay exactly as shipped; verification compares it. Personal content never goes into it. An update replaces it with the new version's copy.
- `seed`: a starter file the owner adapts (`CONTEXT.md`, `memory/glossary.md`, `memory/schema.json`, the folder map, `memory/rules.md`). It must be present; its content is the owner's. An update copies the owner's version across.
- `local`: a starting copy of a file that is the owner's from day one (`memory/index.md`, the generated indexes, `.gitignore`, `START-HERE.md`). Same rules as `seed`.

The `.claude/setup/` files are listed too, but a finished workspace does not keep them: `INSTALL.md` step 12 deletes that folder, so they are the one exception to "must be present". Never edit `MANIFEST.json` to make verification pass.
