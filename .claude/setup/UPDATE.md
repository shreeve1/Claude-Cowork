# A newer version arrived

An update is a first setup into a new folder, migrating from the owner's current workspace. The current workspace stays untouched until the new one is verified; it is the way back (`ROLLBACK.md`).

Words used: the **new Release** is the version that arrived. The **current workspace** is the one the owner uses today. The **new workspace** is a new, empty folder.

## Steps

1. Read the new Release's `CHANGELOG.md` and tell the owner in a few lines what changed.
2. Follow `INSTALL.md` steps 1 to 5 into the new workspace, from the new Release.
3. Follow `MIGRATING.md` with the current workspace as the old setup, with these rules:
   - Shipped files are not migrated: the new Release's copy wins. If the current workspace has a different copy of a shipped `merge` file (the owner or their agent edited `CLAUDE.md` or a shipped skill), make a ledger row for it: what the owner relies on becomes a preference note, the rest is dropped with the owner's OK.
   - Copy across whole: every memory note, `memory/index.md`, `memory/glossary.md` rows the owner added, `memory/rules.md`, `CONTEXT.md`, the folder map (`memory/preferences/document-scaffolding.md`), `.gitignore`, the owner's own skills and every folder from the folder map (documents, research, reports, and the folder named by `client_folder`). After copying, run `hubs.py` and `indexes.py` (`MIGRATING.md` step 4) so hubs match the copied notes.
   - Merge, never copy blindly: `memory/schema.json`, per the `MIGRATING.md` step 2 row. Keep the new Release's topics and keys, add the owner's `client_subjects`, keep their `client_folder`. Without the owner's `client_folder` their notes sit in a folder the new workspace does not look at, and the audit fails.
   - Do not copy `MANIFEST.json`, `CHANGELOG.md`, `START-HERE.md` or anything under `.claude/setup/`; the new Release's copies win.
   - The old ledger (`memory/migration-ledger.md`) is replaced by the new one; keep the old one as `memory/docs/migration-ledger-<date>.md` if the owner wants it.
   - A folder row is fine for a folder copied across whole (for example `memory/workflows/`).
4. If the current workspace has git history and the owner wants to keep it, copy its `.git` folder into the new workspace **after** it is verified, then commit. Ask first: without it the new workspace starts a fresh history.
5. Follow `INSTALL.md` steps 7 to 9 in the new workspace.
6. Tell the owner the current workspace is untouched and can be deleted once they are happy with the new one.
