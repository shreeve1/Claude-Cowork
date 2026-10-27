# Setup

For the owner's agent. You make the placement calls; the owner approves what moves and what is left behind.

## The idea

This Release is a ready workspace: `CLAUDE.md`, skills, memory structure and hooks. The owner ends up with a copy of it that holds their own notes, rules and skills, in the places this structure uses. Their old setup is a source to read, never a shape to keep. Nothing here is a checklist to pass: use judgment, and say what you did.

## First setup

1. Copy every file and folder of the Release, dot folders included, into the owner's new folder. Leave out `.git`. (`robocopy "<release>" "<workspace>" /E /XD .git` on Windows, `rsync -a --exclude .git "<release>/" "<workspace>/"` elsewhere.) Never edit the Release or the old setup.
2. Read `CHANGELOG.md`. Tell the owner in two or three lines what this workspace is.
3. Run the `memory-setup` skill for this workspace, with the old setup as the source (or none). It settles the tracking model, sorts, shows the owner the plan and moves the content.
4. Fit it to the owner (`ADAPTING.md`), then tell the owner in plain words what moved where, what was left behind and why.
5. Make the skills reachable in the owner's app ("Skills in the owner's app" below).
6. Suggest rules ("Suggest rules" below).
7. Remove the setup folder ("Remove the setup folder" below). Always last.

## Where things go

For destinations, read `.claude/skills/memory-setup/where-things-go.md`.

Keep personal content out of shipped files (`CLAUDE.md`, shipped skills, this folder): a later Release replaces them, and memory is never replaced.

## Git and Python

Neither is required, and neither is a first step. Do not probe for them up front and never install anything without the owner's OK; an enterprise computer may not allow it.

- With Git: offer `git init` in the workspace, then `git config core.hooksPath .githooks` (secret scan, memory check, message length). If Python 3.11+ is missing, use `.githooks/nopython` instead, which keeps the message length check. Never use `--no-verify`.
- With Python 3.11+: the `personal-memory` tools run.
- Without either: the workspace still works. Tell the owner what is switched off.

## Skills in the owner's app

`.claude/skills/<name>/` is the one real copy of every skill.

- **Codex, Claude Code** and any app that reads `.claude/skills/` from the workspace: nothing to install. Say so.
- **Claude Cowork** and any app that loads skills only from its own saved list: ask "Save a loader for each skill so Cowork can find them?" Only on a yes, for every folder under `.claude/skills/`:
  1. Take `name` and `description` from its `SKILL.md` frontmatter.
  2. Save a skill with the app's skill-saving tool (`save_skill` in Cowork), same `name` and `description`, body: "Read `.claude/skills/<name>/SKILL.md` from the attached folder and follow it exactly. If it is not present, say so and stop."
  3. Overwrite a loader that already has that name.

  On an update: add loaders for new skills, re-save loaders whose `description` changed, overwrite a removed skill's loader with a body saying it is retired, and leave the owner's own skills alone unless they are in `.claude/skills/`. Tell the owner loaders only work in a session with this folder attached, and updating the folder updates the skills.
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

1. Read the new Release's `CHANGELOG.md` and tell the owner in a few lines what changed.
2. Copy the new Release into a new folder as in step 1 above. The current workspace stays untouched; it is the way back.
3. Bring the owner's content across from the current workspace and judge the rest: shipped files come from the new Release. If the owner or their agent edited a shipped file, keep what the owner relies on as a preference note.
4. Content to copy whole: memory notes, `memory/index.md`, the glossary rows the owner added, `memory/rules.md`, `CONTEXT.md`, the folder map, `.gitignore`, their own skills, and every folder from the folder map.
5. Merge `memory/schema.json` by hand: keep the new Release's topics and keys, add the owner's `client_subjects`, keep their `client_folder`. Without their `client_folder` their notes sit in a folder the new workspace does not look at and the memory audit fails. Run `hubs.py` and `indexes.py` afterwards if Python is present.
6. Do not copy `MANIFEST.json`, `CHANGELOG.md`, `START-HERE.md` or anything under `.claude/setup/`: the new Release's copies win.
7. Keep the old `.git` folder only if the owner wants the history; ask first. Tell the owner the old workspace can be deleted when they are happy.

### Older Releases

Skipping Releases is fine: the steps above work from any earlier Release. Read every `CHANGELOG.md` section newer than the owner's Release (the current workspace's `CHANGELOG.md` or `MANIFEST.json` names it). Then carry these across too:

- **No `memory/rules.md`** (before Release 3): turn each rule the old `CLAUDE.md` or preference notes held into a row in `memory/rules.md` (`personal-memory` "Rules"); every preference note needs a row that loads it.
- **`memory/log.md`** (before Release 3): do not copy it; git keeps the history. Notes marked superseded, or a `Retired` index section: copy only what is still true, rewritten in place.
- **Edited shipped files**, such as an `CLAUDE.md` adapted for one app or edited skills: list each difference, then keep what the owner relies on as a preference note or a decision note, never as an edit to a shipped file. A whole adaptation the owner keeps (for example for Codex) becomes a decision note listing what to re-apply after each update.
- **Gone tools** (`apply-release`, `doctor.py`, the `pre-push` hook, `release-state.json`, a migration ledger): leave them behind and say so. A remote the old workspace pushed to stays only with the owner's yes, recorded as a decision note.

Then run `python .claude/skills/personal-memory/gate.py --memory memory audit` (with Python 3.11+). It also flags leftovers from older Releases: a `memory/log.md`, superseded notes and history lines.

## Going back

Use the previous workspace folder again. Anything written in the new one after the update is not in the old one: list those files by date and copy across only what the owner asks for, using `.claude/skills/memory-setup/where-things-go.md`.

## Other pages

- `ADAPTING.md`: the tracking model, then fitting the workspace to the owner's app and way of working.
- `MANIFEST.md`: what `MANIFEST.json` lists.
- `MARKERS.md`: a stray edition marker line.

## Ground rules

- Ask the owner before dropping content. Never edit, move or delete anything in the owner's old setup.
- Say what you did, in plain words, as you go.
