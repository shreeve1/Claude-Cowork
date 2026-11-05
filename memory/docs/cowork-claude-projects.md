---
title: Claude Projects in Cowork - What a Chat Can Export
summary: What a Cowork chat can export from a Claude app Project: exact instructions/memory, text docs, ID-named files, no chat history.
type: doc
status: promoted
created: 2026-11-02
updated: 2026-11-02
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
- Driving the desktop from `wrk` (2026-11-02): PrintWindow showed only a loading skeleton; foregrounding the window and using CopyFromScreen worked. Call SetProcessDPIAware before reading window coordinates, or clicks miss. Pasting through the clipboard then verifying the draft before sending was reliable.

## Related

- [Project import decisions](memory/decisions/projects/decision-project-import.md) - how imports use this.
- [Claude Cowork Environment](memory/preferences/cowork-environment.md) - Windows desktop control used for the test.

## Notes

- Last reviewed: 2026-11-02
- Source: desktop tests on `wrk` in Openly infographics and Openly design, 2026-11-02.
