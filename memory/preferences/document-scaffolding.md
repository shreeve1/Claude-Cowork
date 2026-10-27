---
title: Documents Go in Folders, Never the Root
summary: No loose files in the workspace root - folder map, naming, what git tracks vs ignores, formats; ask before new top-level folders.
type: preference
status: promoted
created: 2026-10-05
updated: 2026-10-20
topics: [preference, documents, workspace-layout]
---

## Active memory

- The user does not want loose documents in the workspace root. Any report, document, Markdown, HTML, CSV, spreadsheet, or diagram is saved inside a folder; create the folder first if it is missing.
- Folder map (choose by what the file is):
  - `reports/`: finished reports and analyses, `<topic>-YYYY-MM-DD.md`.
  - `research/`: research notes and investigations, `<topic>-YYYY-MM-DD.md`.
  - `notes/`: quick personal notes and scratch lists.
  - `clients/<short>/`: documents about one client, in the subfolders `client_dirs` lists in `memory/schema.json` (`tickets`, `projects`, `procedures`, `meetings`, `templates`). Setup renames `clients` to the owner's `client_folder`.
  - `artifacts/<topic>/`: generated working files (diagrams, spreadsheets, drafts). The default when nothing else fits.
  - `tmp/`: throwaway files, deletable any time.
  - `.handoff/`, `youtube/`: owned by their skills; nothing else goes there.
- Precedence: a path the user names wins, then a skill's own output path, then this map.
- Naming: lowercase, hyphenated, date last as `YYYY-MM-DD`. A task producing several files groups them in one `<topic>-YYYY-MM-DD/` subfolder.
- Git: `memory/`, `research/`, `notes/` and `reports/` are tracked; binaries, raw transcripts, `artifacts/` and `tmp/` are ignored. Check with `git check-ignore -v <path>`. Credentials go nowhere; keep only references to where they live.
- Formats: Markdown for notes, plans, runbooks, handoffs and decisions; CSV for simple tables; Excel only when asked or formatting matters; PowerPoint only for requested slides; HTML previews as `index.html` inside their folder or a `http://localhost:<port>` URL.
- A new top-level folder only when nothing fits, proposed first with its name.
- Loose root files found by an agent are left in place, reported with a proposed home, and moved only when the user says so.
- After creating or updating a document, name its workspace-relative path in the final answer.

## Notes

- Last reviewed: 2026-10-05
- Captured 2026-10-05 from the user's request to add document scaffolding to CLAUDE.md.