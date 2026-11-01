# Claude Cowork setup

For the owner’s agent. This product supports Claude Cowork only. The attached Release is a maintainer distribution, not the folder tree to copy into a user workspace.

## Getting the source

For first setup, migration and updates, the owner downloads the ZIP from `https://github.com/shreeve1/Claude-Cowork`, adds it to the conversation and pastes prompt 1, 2 or 3 from its README. Use that attachment; do not fetch or clone GitHub.

Extract into separate staging, never over an existing workspace. Reject absolute paths, parent traversal and links escaping staging. Locate the repo root inside the ZIP. Use one extracted copy throughout and record its ZIP identity and Release. Missing or unreadable files block setup: ask for a complete attachment or access to a separately extracted copy, not a network workaround.

## What belongs where

- **Maintainer Release:** `.claude/skills/` source, persona libraries, `.claude/setup/`, build/conversion scripts, tests and ready-made `.skill` files. Read these in staging when setup needs them. Never copy the source tree, persona files, builders, tests or package archives into a fresh user workspace.
- **Cowork installation:** show ready-made `.skill` cards from staging with `present_files`; the owner clicks **Save skill**. Do not build, zip, unpack into the workspace or treat source-file copies as installation.
- **User workspace:** the filtered files selected by staged `.claude/cowork/workspace.py`: Cowork-specific `CLAUDE.md`, memory structure and preferences, saved tasks, project scaffolding, standalone Git hooks and the package index for later comparisons. The projected `MANIFEST.json` describes only these files. `memory/README.md` comes from personal-memory’s project scaffold, not the maintainer memory guide.

Owner-added files and skills in an existing workspace stay put. A legacy `.claude/skills/` tree is not permission to delete anything. Identify and preserve custom skills; offer optional cleanup of confirmed shipped sources only after setup works and the owner explicitly approves removal. Never ask about individual unchanged persona files.

## First setup

Use this for a fresh owner workspace or migration from another setup. The old setup stays read-only.

1. **Create the user workspace.** Read the changelog and explain this workspace in two or three lines. With Python, run the staged helper: `python3 "<Release>/.claude/cowork/workspace.py" create "<Release>" "<new empty workspace>"`. It refuses nonempty destinations and source overlap. Without Python, follow the same file-selection and override rules in that helper using file tools; verify the copied files and projected manifest manually. Do not copy the entire Release. Do not add nonexistent projects or facts.
2. **Install in Cowork.** Follow "Skills in Cowork" below. At minimum, verify that personal-memory and memory-setup are installed and their needed files are readable before using them. Setup may read staged instructions to explain/install the packages, but daily work must resolve the installed package, not keep staging as a runtime dependency.
3. **Set up memory and tasks.** Follow installed memory-setup, with the old setup as source or none. Use its tracking-model instructions to settle the owner’s work, useful project folders, memory subjects and procedure topics. Preserve existing notes, task IDs, archives and pending proposals. Show the migration plan and wait for approval before writing migrated content. Use the installed personal-memory templates and recovery helpers. A missing task index is created only at approved setup or task creation; restore existing unfinished rows rather than resetting them.
4. **Adapt and verify.** Follow staged `ADAPTING.md`. Verify the owner’s actual project/file links and memory/task structure. Run installed personal-memory’s helpers and audit, or its disclosed manual checks if permitted. Incomplete legacy procedures need owner-assisted repair and real verification; never invent dates or delete notes to clear an audit. Confirm that no maintainer source or package archives were copied.
5. **Suggest rules.** From the owner’s real work, suggest at most seven useful preferences with reasons and destinations. Ask which they want, save only approved rules through installed personal-memory, and audit again. With little evidence, ask what they use the agent for or skip. Never put personal rules into shipped instructions.
6. **Finish.** Report what moved, what stayed behind, installed versus merely presented cards, checks run and limitations. The setup folder stays in staging, so there is no user setup-folder deletion step. Commit only this session’s changes if Git is available; preserve unrelated staged work.

## Skills in Cowork

Ask once whether to install the workspace’s core skills. On approval, show staged `.claude/cowork/skills/core/*.skill` with `present_files`, in bounded batches. Ask separately whether they also want optional video skills; show staged `video/*.skill` only on yes. Save the answer in the owner’s environment note through personal-memory recovery when editing an existing note.

The owner clicks **Save skill** on each card. A card without that button may mean the organization forbids adding skills: explain that they need their admin, and report installation blocked rather than claiming success. Do not try to bypass the restriction. Keep owner-created installed skills untouched.

For an update, compare against the verified pre-update backup: `python3 "<Release>/.claude/cowork/cowork_skills.py" changed "<backup folder>" --workspace "<Release>"` (add `--video` only if selected). Run from staging; no workspace skill-source tree is needed. Show only listed new/changed packages. Explain `removed`, `moved to video` and legacy-loader notices; the owner manages removals in Cowork settings. With no prior package index or video answer, ask and present the selected sets as first-time installation. Without Python, compare the staged and backup package indexes manually, reporting the limitation.

Resolve personal-memory from its actual Cowork installation for the current session. Verify `SKILL.md`, `tasks.md`, adjacent templates, needed scaffold files and scripts; never assume `/home/james/...`, `~/.claude/skills` or any other app’s install layout. If access is missing, stop affected work and explain what is needed. Installed personal-memory documents the allowed manual checks; unavailable recovery or safe containment still blocks writes.

## Git and Python

Both are optional; check them only when needed and never install tools without approval. Python in Cowork’s sandbox is `python3` (3.10+).

With Git and Python, offer a local repository and `.githooks` configuration. After verifying the installed personal-memory helper folder, set `git config --local cowork.personalMemoryPath "<installed personal-memory folder>"` and `git config core.hooksPath .githooks`. This machine-local helper path may change between sessions: recheck it when needed. The standalone hook scans staged secrets and audits memory through the installed helper; a missing required helper fails explicitly. Do not copy skill sources to satisfy the hook or bypass it. Without Python, use `.githooks/nopython` for message length only, and disclose that automated secret/memory checks are off.

Preserve all unrelated staged/uncommitted files. A Git lock does not prevent a file backup: verify whether it belongs to a live process before proposing removal, and obtain permission. Never commit owner documents or delete a lock just to prepare an update. If an unrelated Git blocker prevents a commit, report it without bypassing hooks.

## A newer version arrived

Update the existing workspace in place; keep the same user folder. Do not run First setup over it.

1. **Stage and identify.** Extract the attached ZIP as above. Read the current Release and newer changelog sections. Run staged `workspace.py plan "<Release>"` to obtain the projected user manifest and each file’s staging source. Compare only projected user files, not the full maintainer manifest. Normalize CRLF to LF for text hashes, as the manifest specifies; line-ending-only changes are not personal edits or individual approval decisions. For legacy workspaces, compare against their installed manifest for ownership, but never import the old source tree into the new projected manifest. Missing ownership evidence means ask before replacement.
2. **Back up before decisions about replacement.** Confirm the location, then create and verify a unique complete backup outside the workspace/staging, including hidden files, `.git`, uncommitted work and both recovery folders. Compare inventory, bytes and required metadata; changed/unreadable files stop the copy. Keep it access-restricted, unchanged and outside recall. Ignore rules are not encryption. No user-workspace changes before verification. Do not bundle this approval with optional videos, instruction replacement or removals.
3. **Plan and check.** Show real owner-content conflicts and proposed removals, grouped in plain language. Preserve owner notes, rules, glossary, `CONTEXT.md`, schema choices, folder map, personal skills, documents, task IDs/history/archive and proposals. Before editing handwritten memory/tasks apply their separate installed recovery protocols; the full backup does not replace them. For edited `CLAUDE.md`, propose preserving owner adaptations in memory and using the projected Cowork instructions, with approval. Check legacy procedures with the new personal-memory helper from staging or its manual checks before replacement; unavailable repairs stop the update. Staged helpers are allowed for this compatibility check only, not as a lasting workspace dependency.
4. **Apply only approved user-file changes.** Use the projected manifest’s `source` paths. Add/replace approved shared user files and standalone hooks, preserving starter/owner files. Reconcile `memory/schema.json` without resetting owner choices; propose optional new topics. Use the Cowork environment seed, preserving owner video selection and useful owner adaptations. Never overwrite owner folders wholesale. No copying `.claude/skills/`, persona libraries, `.skill` archives, setup or maintainer scripts. Retired/legacy sources require separate explicit removal approval; preserve custom skills even if names overlap shipped skills. Keep `.git`, remotes and recovery intact.
5. **Install changed cards.** Follow "Skills in Cowork" against the backup, using the staged packages. Verify the installed personal-memory package again, recheck the hook’s machine-local helper path, and reconcile task startup via installed memory-setup step 3b only with approval. Keep existing task records and routing. Update the workspace’s package index only after selected card installs are confirmed; if incomplete, retain the previous index and report the pending cards rather than calling the update complete.
6. **Verify and finish.** Run installed personal-memory indexes/hubs when needed, audit memory, verify task/project links and protected content against the backup except approved changes, and verify approved shared files against the projected manifest. Save the projected manifest without staging-only `source` fields as the workspace’s new manifest only after successful verification. Preserve owner `START-HERE.md` unless a merge is approved. Commit only this session’s changes, never unrelated staged files or a push. Report the same workspace path, backup, limitations and anything pending. A failed write/check stops the update; offer recovery, not blind continuation. Keep the backup.

### Older Releases

Skipping Releases is allowed; read every intervening changelog section. Missing `memory/rules.md` needs approved routing for existing owner rules, not a reset. Preserve task records and restore active/waiting index rows only through installed personal-memory’s task protocol. Preserve old `memory/log.md`, superseded notes and retired tools in the verified backup; propose cleanup with approval, never delete to clear an audit. Check approved procedures for real risk/approval/verification metadata; unresolved gaps stop affected execution. Confirmed obsolete hooks or sources may be removed only after approval, without discarding custom files. Existing remotes stay unchanged; a push needs current approval.

## Going back

The verified pre-update backup is the way back. Before restoring, identify later work, agree what to preserve, obtain explicit approval and verify a separate copy of the current state. Restore only the approved files/snapshot, then check content, task/memory consistency and installed skill compatibility. Restoring workspace files does not undo Cowork Save skill changes; explain those separately. Keep both backups and never automatically delete newer work or reset Git destructively. A migration can return to its untouched old setup.

## Other pages

- `ADAPTING.md`: owner preferences, projects and installed helper checks.
- `WEEKLY-SWEEP.md`: optional memory maintenance inside Cowork.
- `MANIFEST.md`: maintainer versus projected user manifests.
