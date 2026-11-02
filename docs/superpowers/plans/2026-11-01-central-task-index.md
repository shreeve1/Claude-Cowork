# Central task index implementation plan

**Goal:** One root `tasks/index.md` lists active/waiting records stored with their project or client, without imposing that layout on existing workspaces.

**Approved design:** Owner accepted project/client-local `tasks/<task-name>.md` with a single central index. Adaptation follows actual work, not one migration's checklist. No automatic movement of existing records or owner-specific package patches.

**Implementation calls:** Archive within each record's own task folder; keep root `tasks/` for unassigned and legacy records. IDs are workspace-wide; filenames need only be unique within their own task home. Additional tracked-thing task homes come from the approved document folder map, never arbitrary index links or memory keys alone.

## Checks and execution

- [x] Establish baseline conflict and add failing policy/template tests.
- [x] Update task scope, creation, cross-home discovery/retry/index repair, archival/reopening and recovery safeguards; align templates, skill pointers, setup/adaptation and README. Preserve existing task content and index rows.
- [x] Exercise creation, missing-index lookup/repair, continuation and archival in disposable fixtures; verify files and recovery bytes. Include same-named client/project tasks and archive collisions.
- [x] Rebuild packages; check packaged sources, installed-package tests, manifest and existing suites. Reviewer checks diff against CODING_STANDARDS.md. No push or live installation.
- [x] Save approved convention after memory recovery, audit and commit exact paths.

## Risks checked

Containment and escaping-symlink checks apply to every home and recovery path. Index pointers neither authorize work nor widen approved homes. Missing/stale indexes must not hide distributed or legacy records. Duplicate IDs and interrupted moves must not create new tasks. Existing layouts stay unless changes are approved.
