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

## 10. Install or update the skills in the owner's app

`.claude/skills/<name>/` is the one real copy of every skill. Whether the app finds it depends on the app:

- **Claude Code** (terminal, IDE, or the desktop Code tab): it reads `.claude/skills/` from the workspace itself. Nothing to install. Say so and go to step 11.
- **Claude Cowork** (and any app that loads skills only from its own saved list): each skill needs a small loader saved to the owner's account. Ask the owner first: "Save a loader for each skill so Cowork can find them?" Only on a yes, for every folder under `.claude/skills/`:
  1. Read its `SKILL.md` and take `name` and `description` from the frontmatter.
  2. Save a skill with the app's skill-saving tool (`save_skill` in Cowork), same `name` and `description`, with this body: "Read `.claude/skills/<name>/SKILL.md` from the attached folder and follow it exactly. If it is not present, say so and stop."
  3. If a loader with that name already exists, overwrite it.

  On an update, also:
  - Add loaders for skills that are new.
  - Re-save loaders whose `description` changed.
  - Overwrite the loader of a skill that was removed so its body says it is retired and tells the owner to ignore it.
  - Leave the owner's own skills alone unless they are in `.claude/skills/`.

  Tell the owner the loaders only work in a session with this workspace folder attached, and that the real skill text stays in the folder, so updating the folder updates the skills.
- **Another app:** follow `ADAPTING.md` Part 1 to point it at `.claude/skills/`, and say what you could not do.

## 11. Remove the setup folder (last)

Do this only at the very end: after the owner has finished adapting with `ADAPTING.md` or said they do not want to. Tell the owner you are removing `.claude/setup/` from the workspace, then delete that folder in the workspace only. Never delete it from the Release or touch the old setup. The workspace does not need it: an update reads `UPDATE.md` from the new Release. If Git is present, commit the removal (`git add -A`, `git commit -m "setup: remove setup folder"`); the hooks run, never use `--no-verify`.
