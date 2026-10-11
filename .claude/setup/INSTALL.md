# First setup

Read `README.md` in this folder first: the result is fixed, and this procedure is not done until the check passes. Do every step in order. Do not skip, reorder or merge steps.

Words used: the **Release** is the folder or repo you received (this one). The **workspace** is the new, empty folder the owner chose. The **old setup** is whatever the owner used before (a folder, an instructions file, notes); there may be none.

## 1. Check what this computer has

Run `git --version` and `python3 --version` (Windows also try `py -3 --version`). Write down the results; they decide steps 4 and 7.

- Git present: the workspace gets version history and its commits are checked.
- Python 3.11 or newer present: the commit checks, memory tools and `doctor.py` run.
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

## 7. Run the check

- With Python: `python .claude/setup/doctor.py --migration`
- Windows without Python: `powershell -ExecutionPolicy Bypass -File .claude\setup\doctor.ps1 -Migration`

Fix every `FIX` line and run it again. Repeat until it prints `All checks passed.` Never edit `MANIFEST.json`, the check scripts or the ledger format to make it pass. If a rule seems wrong for this owner, stop and tell the owner.

## 8. Commit (only if Git is present)

Show the owner `git status`, then commit everything with the owner's OK, for example `git add -A` and `git commit -m "workspace set up"`. The hooks run; never use `--no-verify`.

## 9. Tell the owner

Say in plain words: setup passed the check, what moved where (one line per group from the ledger), anything dropped and why, and what is switched off on this computer (Git, Python). Then offer `ADAPTING.md`.
