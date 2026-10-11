# Setup

These instructions are for the owner's agent. Follow them exactly; the owner decides at every marked point.

## The result is fixed

When setup is done, the owner's workspace has exactly this workspace's structure: every shipped file present and unchanged, the shipped folders, the shipped skills. The owner's own information (notes, rules, preferences, names, their own skills) is moved into that structure, in the places `MIGRATING.md` names.

The owner's old setup is a source to read from. It is never a shape to keep. Do not:

- keep the old folder layout, old config files or old skill copies alongside the new ones;
- leave out, trim or "simplify" shipped files, skills or folders because the old setup did not have them;
- paste personal rules into shipped files (`CLAUDE.md`, a shipped skill); they go to memory;
- stop halfway and call it done.

Verify this against "What must be true" in `MIGRATING.md`. Setup is not done until every item holds. If you believe a rule is wrong for this owner, stop and tell the owner; do not work around it.

## Which document to open

- First setup: `INSTALL.md`, then `MIGRATING.md`.
- A newer version arrived: `UPDATE.md`.
- The new workspace does not work and the owner wants the old one back: `ROLLBACK.md`.
- After setup, fitting it to the owner's app and way of working: `ADAPTING.md`.
- What is inside a version: `MANIFEST.md`.
- Found a stray edition marker line: `MARKERS.md`.
- Proving it all works on a test system: `CHECKLIST.md`.

## Ground rules

- Ask the owner before dropping anything; record every item in the migration ledger.
- Never edit, move or delete anything in the owner's old setup. It is read only.
- Never skip the git hooks (`--no-verify`).
