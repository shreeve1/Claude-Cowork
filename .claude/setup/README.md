# Setup

For the owner's agent. You make the placement calls; the owner approves what moves and what is left behind.

## The idea

This Release is a ready workspace: `CLAUDE.md`, skills, memory structure and hooks. First setup and migration create a workspace holding the owner’s notes, rules and skills in the places this structure uses. An update refreshes an existing workspace in place after a verified backup. During migration the old setup is a source to read, never a shape to keep. Use judgment, and say what you did.

## Getting the source

The public source is `https://github.com/shreeve1/Claude-Cowork`. Only first-time setup asks the owner to download a copy. For migration or an update, read this guide from that repo, fetch a complete copy into a separate staging folder, and follow all linked setup instructions from that same revision. Record the commit used; do not mix files from different revisions. A fetched guide describes the process, not permission to change the owner’s files.

Check that the source has `MANIFEST.json`, the setup guide, referenced skills, and ready-made Cowork packages. If network access or a complete fetch is unavailable, stop before changing the workspace and explain the blocker. Do not require the owner to prepare another downloaded copy. Never extract the repo over an existing workspace.

## First setup

During setup, "run the `<name>` skill" means open `.claude/skills/<name>/SKILL.md` in the new workspace and follow it. No skill needs to be installed in the owner's app first; in Claude Cowork the installs happen at step 5.

1. Copy every file and folder of the Release, dot folders included, into the owner's new folder. Leave out `.git`, `.memory-recovery/` and `.task-recovery/`. (`robocopy "<release>" "<workspace>" /E /XD .git .memory-recovery .task-recovery` on Windows, `rsync -a --exclude .git --exclude .memory-recovery --exclude .task-recovery "<release>/" "<workspace>/"` elsewhere; in Claude Cowork's Bash sandbox use `tar -C "<release>" --exclude=./.git --exclude=./.memory-recovery --exclude=./.task-recovery -cf - . | tar -C "<workspace>" -xf -`, with a new empty destination and Bash pipefail enabled.) Never edit the Release or the old setup.
2. Read `CHANGELOG.md`. Tell the owner in two or three lines what this workspace is.
3. Read and follow `.claude/skills/memory-setup/SKILL.md` for this workspace, with the old setup as the source (or none). It settles the tracking model, sorts, shows the owner the plan and moves the content.
4. Fit it to the owner (`ADAPTING.md`), then tell the owner in plain words what moved where, what was left behind and why.
5. Make the skills reachable in the owner's app ("Skills in the owner's app" below).
6. Suggest rules ("Suggest rules" below).
7. Remove the setup folder ("Remove the setup folder" below). Always last.

## Projects and procedures

Before filing old notes, settle the purpose-led layout in `memory-setup/tracking-model.md` (under `.claude/skills/`). For non-client work, default to `projects/<short>/README.md` and useful project folders, not ticket folders with a new label. During setup, read `.claude/skills/personal-memory/supporting-templates.md` from this new workspace for the README; after installation, the updated personal-memory package includes the same format. Keep the project workspace attached in Cowork. Include independent projects alongside clients when needed. Empty workflow indexes are normal; propose suitable schema topics during setup, but save executable procedures only after real verification and owner approval.

## Saved tasks

The selected personal-memory install provides tasks.md and its adjacent record/index and supporting templates. At approved setup, create an absent `tasks/index.md` through memory-setup step 3a: restore rows for existing active/waiting records, using an empty index only when none exist. Leave existing tasks/index/archive/proposals intact; routine startup reads create nothing. Startup reads the compact index; individual records load on demand. First creation or explicit pickup authorizes bookkeeping, not consequential actions. Complete archives the file before removing its row. All lookup stays in the current workspace; templates require neither an external authoring skill nor these setup/spec docs.

## Where things go

For destinations, read `.claude/skills/memory-setup/where-things-go.md`.

Keep personal content out of shipped files (`CLAUDE.md`, shipped skills, this folder): a later Release replaces them, and memory is never replaced.

## Git and Python

Neither is required, and neither is a first step. Do not probe for them up front and never install anything without the owner's OK; an enterprise computer may not allow it.

- With Git: offer `git init` in the workspace, then `git config core.hooksPath .githooks` (secret scan, memory check, message length). If Python 3.10+ is missing, use `.githooks/nopython` instead, which keeps the message length check. Never use `--no-verify`.
- With Python 3.10+ (Claude Cowork's Bash sandbox has it): the `personal-memory` tools run.
- Without either: the workspace still works. Tell the owner what is switched off.

## Skills in the owner's app

`.claude/skills/<name>/` is the one real copy of every skill.

- **Codex, Claude Code** and any app that reads `.claude/skills/` from the workspace: nothing to install. Say so.
- **Claude Cowork** loads skills only from the owner's own Cowork, so install them there. They are ready-made: `.claude/cowork/skills/core/` holds a `.skill` file for every core skill, `.claude/cowork/skills/video/` the optional video skills. Install these files as they are; do not build or zip skills yourself. Ask once: "Install this workspace's skills into your Cowork? I'll show a card for each skill and you click **Save skill** on each." On a yes:
  1. First setup: ask once, "Do you also want the video skills (about 27, some large)?", and change the "Video skills installed" line in `memory/preferences/cowork-environment.md` to yes or no. Show every `.skill` file in `.claude/cowork/skills/core/` (and in `video/` on a yes) with `present_files`, in one call or a few batches.
  2. Update: use the verified pre-update backup as `<backup folder>` below. `memory/preferences/cowork-environment.md` comes from the new version; preserve only the "Video skills installed" answer from the backup’s copy. If the backup has no such line or says "not asked yet", do step 1 as for a first setup. Otherwise, in the Bash sandbox, from the updated workspace, run `python3 .claude/cowork/cowork_skills.py changed "<backup folder>"` (the backup containing the old `.claude/` tree, never the updated workspace; add `--video` if the answer is yes). Show only the `.skill` files it lists. For each `removed: <name>` line, tell the owner to delete that skill in Cowork's skill settings. For each `moved to video: <name>` line, tell the owner that skill is now an optional video skill: they can keep it, but it will no longer be updated unless they add the video skills. If it prints `loaders: yes`, the old setup used loader skills: saving the new cards replaces them, and any other old loader the owner did not get a card for (for example video skills) should be deleted the same way.
  3. Tell the owner to click **Save skill** on each card. A card without that button means their organisation does not allow adding skills: they ask their admin, then you show the cards again.

  Leave the owner's own skills alone. Tell the owner the skills read and write this workspace, so keep this folder attached in Cowork.
- **Another app:** point it at `.claude/skills/` (`ADAPTING.md` Part 1) and say what you could not do.

## Suggest rules

After the skills step, before removing the setup folder.

1. **Look.** Read `memory/` notes, the folders from the folder map, the owner's own skills, `CONTEXT.md`, what the owner said during setup and, with Git, `git log --stat`. Change nothing yet.
2. **Infer.** The main kinds of work, what repeats, which skills fit or do not, and any rule the owner keeps restating.
3. **Suggest.** At most 7, in one message. For each: the rule in one sentence, why it fits (what you saw), and where it goes. A rule is a preference note in `memory/preferences/` plus a `memory/rules.md` row pointing to it; a skill to leave alone is a `memory/rules.md` row (When: Always, Note: "never use skill `<name>`"). Never put a rule in `CLAUDE.md` or another shipped file.
4. **Ask once.** "Which of these do you want?" Save only those, with `personal-memory`, then run the memory audit if Python is present.
5. **Thin evidence.** With little to go on, invent nothing: ask what they mostly use an agent for and how answers should read, then suggest from that, or skip if they decline.

Never put secrets, client names or personal details into a suggested rule. Say what you saved, or that nothing was saved.

## Remove the setup folder

Only at the very end, after the owner has finished `ADAPTING.md` or declined it. Tell the owner, then delete `.claude/setup/` in the workspace only, never in the Release or the old setup. An update reads its setup from the new Release. With Git, commit the removal; the hooks run, never `--no-verify`.

## A newer version arrived

Update the existing workspace in place; the owner keeps using the same folder. Do not run First setup over it or copy the whole Release onto it.

1. **Stage and compare.** Fetch the source as described in "Getting the source". Read the installed `MANIFEST.json` or `CHANGELOG.md`, then every newer changelog section. Explain what changed. Use the installed and new manifests to identify shipped files, owner changes and filename collisions. If the installed manifest is missing, treat ownership as unknown rather than assuming files are safe to overwrite.
2. **Back up before writing.** With the owner’s approval for the backup location, make a unique complete backup outside the workspace and staging folder, with space for hidden files, `.git`, uncommitted work, `.memory-recovery/` and `.task-recovery/`. Preserve file contents and required metadata; verify the path inventory and file bytes against the current workspace. Stop if files are unreadable, change during the copy, or cannot be verified. Keep this backup unchanged, access-restricted and outside routine recall. Ignore rules do not encrypt it. Record its path and the source revision. No workspace file changes before verification succeeds.
3. **Show the plan.** List shipped files to add or replace and any proposed removals. Preserve owner-added skills and files, and ask before replacing edited shipped files or conflicting paths. Keep the owner’s useful adaptations as approved preference or decision notes before replacement. If newer files collide with owner content or ownership is unclear, stop for a decision; never infer permission from a manifest entry. Retired shipped files need explicit removal approval and remain recoverable from the backup.
4. **Preserve owner content.** Leave memory notes, `memory/index.md`, glossary rows, `memory/rules.md`, `CONTEXT.md`, the folder map, `.gitignore`, personal skills, all `tasks/` records and archives, pending proposals, project files and every document folder intact. Do not reset them to the Release’s starter copies. The exception is `memory/preferences/cowork-environment.md`: use the new version after preserving its previous content through personal-memory recovery, then restore the owner’s "Video skills installed" answer. Keep `.git`, remotes and both recovery folders in place. Retain `/.memory-recovery/` and `/.task-recovery/` in `.gitignore`.
5. **Check compatibility before replacement.** Run the staged personal-memory procedure checks against the existing workspace: `python3 "<staged Release>/.claude/skills/personal-memory/gate.py" --memory memory procedures`, from the workspace root (or compare against the staged Procedure File template without Python). Report incomplete legacy procedures and ask for owner-assisted repair based on real events. Never invent dates or delete notes to pass. If repair cannot happen now, stop before applying the update. Also follow "Older Releases" for skipped versions.
6. **Apply approved changes only.** Replace or add approved shipped files from the staged Release, including the shipped memory layout/templates and Cowork packages, without copying starter notes or whole directories onto owner content. Use the new Release’s `MANIFEST.json` and `CHANGELOG.md`; preserve the owner’s `START-HERE.md`, merging any necessary new guidance with approval. Do not install `.claude/setup/` into the workspace; continue reading it from staging. Preserve previous hand-written memory and task content using their respective recovery protocols before any approved edit; the full backup does not replace these checks. Reconcile saved-task startup via staged `memory-setup` step 3b with owner approval, retaining unrelated rules and every task ID, index row and work history.
7. **Reconcile the schema.** Preserve the owner’s `client_folder` (absence in an older schema means `clients`), `client_subjects`, `client_dirs` (including an empty list), `topics` and `topic_dirs`; add new Release keys only where absent. Explain new topics as optional additions and get approval before adding them; never reset owner choices or remove values used by notes. Keep project READMEs/files and the folder map, including independent `projects/` beside `clients/`. Check changed integrations for compatibility rather than renaming data to suit them. Run `hubs.py` and `indexes.py` from the updated personal-memory skill if Python is present; review resulting links. Otherwise reconcile and verify manually, disclosing automated checks not run.
8. **Update installed skills.** Follow "Skills in the owner’s app", comparing against the verified backup rather than the updated workspace. Show only new or changed cards for the selected skill sets, and explain removed or reclassified skills. The owner still clicks **Save skill**; changing source files alone does not update Cowork’s installed copies.
9. **Verify and finish.** Run the memory audit with the updated personal-memory tools, check project and task links, and confirm protected owner files and task history match the backup except for approved edits. Check that replaced shipped files match the selected Release. Disclose manual checks or any blocked skill installs; do not call a partial update complete. Commit only this session’s changes when Git is available; never push without approval. Report what changed, anything left unresolved, the backup path and how to go back. The workspace path stays the same. Keep the backup; never delete it automatically. If any write or verification fails, stop, report the partial state and offer recovery rather than continuing blindly.

### Older Releases

Skipping Releases is fine: the steps above work from any earlier Release. Read every `CHANGELOG.md` section newer than the owner's Release (the current workspace's `CHANGELOG.md` or `MANIFEST.json` names it). Then reconcile these legacy cases in place, preserving previous content and asking before removals:

- **No `memory/rules.md`** (before Release 3): turn each rule the old `CLAUDE.md` or preference notes held into a row in `memory/rules.md` (`personal-memory` "Rules"); every preference note needs a row that loads it.
- **`memory/log.md`** (before Release 3): preserve it in the verified backup, then ask before removing it from active memory. Git alone may not contain uncommitted content. For superseded notes or a `Retired` index section, propose keeping only what is still true and get approval before changing standing guidance.
- **Edited shipped files**, such as a `CLAUDE.md` adapted for one app or edited skills: list each difference, then keep what the owner relies on as a preference note or a decision note, never as an edit to a shipped file. A whole adaptation the owner keeps (for example for Codex) becomes a decision note listing what to re-apply after each update.
- **Gone tools** (`apply-release`, `doctor.py`, the `pre-push` hook, `release-state.json`, a migration ledger): identify leftovers and propose removal; remove only with approval and keep the backup. Keep existing remotes unchanged; any later push still requires the owner’s approval.

Then run `python3 .claude/skills/personal-memory/gate.py --memory memory audit` (with Python 3.10+). It also flags leftovers from older Releases: a `memory/log.md`, superseded notes and history lines. Ask before removing legacy files; retain them in the backup.

## Going back

For an in-place update, the verified pre-update backup is the way back. Before restoring, list differences and work created since the update, agree what must be preserved, and obtain the owner’s explicit approval. Preserve and verify the current state separately before any overwrite; keep both backups. Restore only the approved files or full snapshot, then verify restored contents and task/memory consistency. Never automatically delete newer work or run a destructive Git reset. A migration can still go back by using its untouched old setup.

## Other pages

- `ADAPTING.md`: the tracking model, then fitting the workspace to the owner's app and way of working.
- `MANIFEST.md`: what `MANIFEST.json` lists.
- `MARKERS.md`: a stray edition marker line.

## Ground rules

- Ask the owner before dropping content. Migration leaves the old setup untouched; updates change only the approved current workspace after a verified backup. Keep the staged Release and backup unchanged.
- Say what you did, in plain words, as you go.
