# First setup

Read `README.md` in this folder first: the result is fixed, and this procedure is not done until every item under "What must be true" in `MIGRATING.md` is verified. Do every step in order. Do not skip, reorder or merge steps.

Words used: the **Release** is the folder or repo you received (this one). The **workspace** is the new, empty folder the owner chose. The **old setup** is whatever the owner used before (a folder, an instructions file, notes); there may be none.

## 1. Check what this computer has

Run `git --version` and `python3 --version` (Windows also try `py -3 --version`). Write down the results; they decide steps 4 and 7.

- Git present: the workspace gets version history and its commits are checked.
- Python 3.11 or newer present: the commit checks and memory tools run.
- Neither is required. Never install anything without the owner's OK. In an enterprise environment the owner may not be allowed to; that is fine.

## 2. Copy the Release into the workspace

Copy every file and folder of the Release into the workspace, including folders whose names start with a dot (`.claude`, `.githooks`). Do **not** copy `.git`. Do not leave anything out, rename anything or change any file.

- PowerShell: `robocopy "<release>" "<workspace>" /E /XD .git` (exit codes 0 to 7 mean success).
- macOS/Linux: `rsync -a --exclude .git "<release>/" "<workspace>/"`

From here on, work only inside the workspace. Never edit the Release folder or the old setup.

## 3. Read the version notes

Read `CHANGELOG.md` in the workspace. Tell the owner in two or three lines what this workspace is.

## 4. Version history (only if Git is present)

In the workspace: `git init`, then switch on the hooks:

- Python 3.11+ present: `git config core.hooksPath .githooks` (secret scan, memory check, push protection, message length).
- No Python: `git config core.hooksPath .githooks/nopython` (push protection and message length only; the secret scan and memory check need Python). Never leave the hooks off: the push protection is what keeps `memory/` and client notes off any remote.

## 6. Tracking model, then migrate

First do `ADAPTING.md` "Tracking model": what people or things the owner keeps coming back to, their short names, subjects and hub rule. Migrated facts about them need that home.

Then follow `MIGRATING.md` from step 1 to the end, including writing `memory/migration-ledger.md`. If the owner has no old setup, the ledger has one row with outcome `none`.

## 7. Verify

Go through every item under "What must be true" in `MIGRATING.md`. Compare each shipped file with `MANIFEST.json` (class and sha256). Fix every failure and verify again. Never edit `MANIFEST.json` or the ledger format to make it pass. If a rule seems wrong for this owner, stop and tell the owner.

## 8. Commit (only if Git is present)

Show the owner `git status`, then commit everything with the owner's OK, for example `git add -A` and `git commit -m "workspace set up"`. The hooks run; never use `--no-verify`.

## 9. Tell the owner

Say in plain words: setup is verified, what moved where (one line per group from the ledger), anything dropped and why, and what is switched off on this computer (Git, Python). Then offer `ADAPTING.md`.

## 10. Offer auto-commit (only if Git is present)

Ask the owner: "Commit your changes automatically every time I finish a turn? It never pushes." Only on a yes:

1. Copy `.claude/setup/autocommit.sh` to `.claude/hooks/autocommit.sh` (create the folder). Do this now: step 11 deletes the setup folder.
2. Register it as a `Stop` hook in the workspace's `.claude/settings.json`, merging with any hooks already there:

   ```json
   {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "bash .claude/hooks/autocommit.sh"}]}]}}
   ```

3. Tell the owner it needs `bash` on the path (Git for Windows includes it), that it commits everything with `auto: <time>` messages, never pushes, and leaves changes uncommitted if a git hook rejects them. Removing the `Stop` entry turns it off.

Only Claude Code supports this. For another agent app, skip it and say so.

## 11. Remove the setup folder (last)

Do this only at the very end: after the owner has finished adapting with `ADAPTING.md` or said they do not want to. Tell the owner you are removing `.claude/setup/` from the workspace, then delete that folder in the workspace only. Never delete it from the Release or touch the old setup. The workspace does not need it: an update reads `UPDATE.md` from the new Release. If Git is present, commit the removal (`git add -A`, `git commit -m "setup: remove setup folder"`); the hooks run, never use `--no-verify`.
