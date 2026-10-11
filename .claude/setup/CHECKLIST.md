# Test-system checklist

Run this once with the owner, on a scratch folder or test machine, before real use. `python` means `py -3` or `python3` if needed. Tick each box only after seeing it work.

## Install

- [ ] First setup into an empty scratch folder by following `INSTALL.md`, migrating from a copy of the owner's real old setup.
- [ ] Every item under "What must be true" in `MIGRATING.md` is verified.
- [ ] Verification catches a mistake: delete one shipped skill folder, see it flagged against `MANIFEST.json`, restore it.
- [ ] In Cowork with a yes: every folder under `.claude/skills/` has a saved loader with the same name and description, and a skill runs from a session with the workspace attached. After an update: new skills have loaders, changed descriptions are re-saved, removed skills' loaders say they are retired.
- [ ] Before the setup folder is removed, the owner was shown at most 7 suggested rules with the reason for each, only the ones they picked were saved (preference note plus `memory/rules.md` row), and nothing went into `CLAUDE.md`. With little evidence, the agent asked two questions instead of inventing rules.
- [ ] After adapting (or declining it), `.claude/setup/` is deleted from the workspace (`INSTALL.md` step 12), the Release is unchanged, and with Git the removal is committed.
- [ ] If Git and Python are present: a throwaway commit touching a `memory/` note runs the audit; undo it (`git reset --soft HEAD~1` and discard the change).

## Updates

- [ ] Add a preference note and a document in the scratch workspace.
- [ ] Set up a newer version into a second scratch folder by following `UPDATE.md`; every item under "What must be true" is verified, and the note and document are there.
- [ ] The first scratch workspace is unchanged.

## Tracking model

- [ ] The owner's tracked things, subjects, folder name (`client_folder`) and hub rule are set (`ADAPTING.md`, "Tracking model"), or the owner has none and `client_subjects` is empty.
- [ ] One real note exists for one thing, its hub lists it, and `python .claude/skills/personal-memory/gate.py --memory memory audit` passes.
- [ ] With a changed `client_folder`: a note under `memory/<client_folder>/`, `hubs.py` writes the hub under `memory/<client_folder>/_hubs/`, and no `memory/clients/` folder appears.
- [ ] Asked about that thing in a fresh session, the agent reads its hub.

## Windows

- [ ] If Git and Python are present: hooks run when committing from PowerShell and from Git Bash.
- [ ] Without Python: `core.hooksPath` is `.githooks/nopython`; a test push of a `memory/` note to a scratch remote is refused.

## Harness

- [ ] The owner's agent app reads `CLAUDE.md` and finds the skills (`ADAPTING.md`).
- [ ] A start-of-day loop, if the owner wants one, runs on a test day before a real one (`startday-spec`, `references/adaptation-list.md` "Before a first real day").
- [ ] If a runner is used: one triggered run writes a file in this workspace, and the owner knows how to pause it (`startday-spec`, `references/runners.md`).
