---
title: Claude Projects in Cowork - Export and Import Decisions
summary: What a Cowork chat can export from a Claude app Project, and James's decisions on sorted import and project skills.
type: doc
status: promoted
created: 2026-11-02
updated: 2026-11-05
topics: [tools, projects]
---

## Active memory

- A Cowork chat with a Claude app Project added (from the project page, or a new chat's project picker: "Add project context from ...") gets a local copy under `AppData\Local\Claude-Data\...\local-agent-mode-sessions\...\.project-cache\<project id>\`: `metadata.json` (id, name, description, instructions, sync time), `memory.md`, `docs/` (text documents) and `files/` (images, PDFs).
- The chat can copy these out exactly: instructions and memory are byte-for-byte; Markdown docs arrive intact.
- Word documents arrive as extracted text only (`.md`); originals are not in the copy.
- Images and PDFs are exact bytes but named by ID; nothing maps them back to original names. Some `.png` files are really JPEG.
- Chat history is not available; only the project's memory summary reflects it.
- With a workspace folder also attached (**Add folder**), the chat can write the project into the workspace. Verified: 31 files, 147 MB, checksums identical.
- Without an attached folder, written files land in the session's hidden `outputs/` folder.
- Not yet tested: several projects in one chat.
- A new chat reuses the last attached folder; check the attachment before importing. `itastack - Copy` is the old Codex layout (no `CLAUDE.md`, `projects/` or Git), so the import correctly refuses it; test imports use a fresh workspace from `workspace.py create`.
- Native import test, 2026-11-05: Openly design imported into `Documents\cowork-project-test`; all 27 kept files byte-identical to the project copy; project skill saved and auto-loaded in a fresh chat. Cowork could not commit there because that test workspace skipped setup (no hook path; rules name the uninstalled `meeting` skill) and its sandbox left a stale `.git/index.lock` it could not delete.
- Driving the desktop from `wrk` (2026-11-02): PrintWindow showed only a loading skeleton; foregrounding the window and using CopyFromScreen worked. Call SetProcessDPIAware before reading window coordinates, or clicks miss. Pasting through the clipboard then verifying the draft before sending was reliable.

Owner decisions (James, 2026-11-02; kept here because `memory/decisions/index.md` ships to users):

- **Sorted import** (instructions, memory and files reviewed and approved), not a raw copy.
- Import is **offered as the last step** of setup and migration, after adapting, and any time later; many projects allowed.
- Filed wherever the workspace's setup keeps work (projects, clients or the owner's word); never assume client or project.
- **Both shapes**: every project gets a folder opened by one shared `project-import` skill (renamed from `project` by James, 2026-11-05); a project with repeatable steps may also get its own skill.
- **Exception to "never build skills for end users"**: import-made project skills, each owner-approved, installed with **Save skill**.
- Setup and migration explain creating skills inside Cowork.
- Design (approved): `docs/superpowers/specs/2026-11-02-project-skill-design.md`; plan: `docs/superpowers/plans/2026-11-02-project-skill.md`.

## Related

- [Claude Cowork Environment](memory/preferences/cowork-environment.md) - Windows desktop control used for the test.

## Notes

- Last reviewed: 2026-11-02
- Source: desktop tests on `wrk` in Openly infographics and Openly design, 2026-11-02.
