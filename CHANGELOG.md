# Changelog

## Release 3

- Setup works differently. Your agent copies this version into a new folder, moves your own notes, rules and skills in, and runs a check. It is done only when the check passes. `START-HERE.md` at the top has the one message to give your agent.
- Updates work the same way: a fresh copy of the new version, with your content moved across from your current workspace. Your current workspace is left untouched until the new one passes, so going back is just using the old folder.
- The `apply-release` skill is gone; you no longer run anything to install or update.
- New `.claude/setup/MIGRATING.md`: your agent lists everything in your old setup in a migration ledger, asks you once per group where it goes, and never drops anything without your OK. Personal rules go into memory, not into shipped files, so updates never overwrite them.
- New check: `.claude/setup/doctor.py --migration`, or `doctor.ps1 -Migration` on a Windows computer without Python. Python and Git are no longer required. Without Python the secret scan and memory check cannot run, but the push protection stays on (`.githooks/nopython`), so your notes never reach a remote.
- The Release brings a ready `memory/index.md`, the memory indexes and a `.gitignore`, so your agent no longer writes them by hand.
- `ADAPTING.md` now starts with a "Tracking model" step, run before `MIGRATING.md`: your agent asks what people or things you keep coming back to and what you need remembered, then sets up short names, note subjects, a rule that loads them and a folder named in your own word (for example `students`, set with `client_folder` in `memory/schema.json`). Setup and migration use it, so existing notes land in the right place. A starter rule "Work on one client" now ships in `memory/rules.md`; setup renames or removes it.
- `ADAPTING.md` also walks through making the workspace fit how you work: skills you won't use, answer style, folders, names and rules. Rules that differ from `CLAUDE.md` become preference notes.
- `startday-spec` now builds a loop from modules you pick: work items, meeting transcripts from a folder, and files or pages to watch (new `scripts/watch.py`). The loop is optional: type `startday` yourself, or pick a runner (a local scheduled task in Claude Desktop or Codex, Claude Code `/loop`, omp `/loop`). Cowork scheduled tasks run remotely by default and cannot see your workspace; the spec says when a local run works.
- The team-only Operator Profile page is no longer in your copy.
- Your agent reads less when it saves a memory. The `personal-memory` skill is shorter: setup, recovering missing files and a full health check moved to `.claude/skills/personal-memory/reference.md` (opened only for those), and text that repeated `memory/README.md` is gone. Saving a note, including a client note, needs nothing in the reference file. Nothing it remembers changed. The memory index is read at the start of every session, so `gate.py compact` now strips the extra spaces an editor adds to its table, and the audit warns when they appear.
- To bring it in, give your agent this version and follow `.claude/setup/UPDATE.md`.

## Release 2

- No change to your files. The Release folder is rebuilt so its version moves with the team edition.

## Release 1

- friends edition export.
