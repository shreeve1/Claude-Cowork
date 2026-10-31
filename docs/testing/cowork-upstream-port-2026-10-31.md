# Cowork upstream port verification

Ported starter-agent through `6259baf` onto Cowork baseline `aeffc4c`. Verification ran on Linux with Python 3.12.3. This is a source/package port, not a native Cowork installation or a new numbered upstream Release.

## Coverage and preservation

- All 39 applicable files changed upstream since `d05ec95` are present in the Cowork layout. Six internal implementation plans/specs remain upstream; the two historical verification records are included verbatim under `docs/testing/`.
- The upstream worktree stayed unchanged. Cowork's source tree received targeted additions/updates with no deletions. Its draw.io implementation, owner notes, migration-ledger index entry, environment routing and maintainer converter were retained.
- Existing hand-written memory was preserved byte-for-byte under ignored `.memory-recovery/` before modification. Neither upstream recovery nor tool caches were imported.
- A new conversion from the current upstream folder completed without warnings or drift checks. `KEEP_WORKSPACE` now checks actual source bytes instead of stale upstream manifest hashes.
- No root `AGENTS.md` or `.agents/` directory remains. Historical test receipts, conversion tooling, the web-standard reference library and explicit other-app/exclusion documentation retain intentional references.

## Deterministic checks

All 252 shipped Python unit tests passed in the ported repository:

| Suite | Tests |
| --- | ---: |
| Conversion and Cowork packaging | 36 |
| Cowork draw.io | 15 |
| Meeting | 16 |
| Memory setup | 6 |
| Personal memory | 161 |
| Startday | 9 |
| Git hooks | 9 |

The Remotion script test directory contains no unittest tests and is not counted as test coverage. Unchanged optional video JavaScript suites were not run.

The memory audit, generated workflow/decision index check, client hub check and procedure collection check passed. All 45 shipped Python files parsed using Python 3.10 grammar; this is not a Python 3.10 runtime test. The root `CLAUDE.md` is 15,020 bytes, below the existing 16,384-byte audit limit.

The staged whitespace check exposed an inherited extra blank line at the end of the new task template; it was removed in the template and its conversion rule before committing.

Regression tests cover newly listed memory/task files, recovery/runtime-state exclusion even when manifest-listed, source drift hidden by a stale manifest, CRLF hash normalization, Cowork environment routing, the upload-safe task description, unchanged historical receipts and self-contained packaged task/recovery support.

## Packages and fresh-project smoke test

- All 48 packages built successfully. Archive integrity checks passed, and every packaged member matched its current source bytes with the build's line-ending normalization.
- Every listed manifest file matched its hash.
- Only five core packages changed: `adhd`, `brainstorm-idea`, `memory-setup`, `personal-memory` and `startday-spec`. No video package changed.
- Extracted the core packages into a separate installed-skills directory, then created a fresh project with spaces and Unicode in its path, no Git and no project-local skills. Generated memory indexes/hubs, ran the audit and procedure checker, and created an exact-byte memory snapshot using the extracted helpers. The optional task index remained absent; no task recovery was created by a read.
- The first smoke fixture lacked `CONTEXT.md`, which its copied scaffold rules referenced, so its audit failed. A fresh complete fixture passed. The first full candidate test run lacked Git, so the task Git-ignore regression failed; after initializing Git only in that scratch candidate, all 161 personal-memory tests passed. Neither failure was concealed or bypassed.

## Limits

Native Claude Cowork, its Save skill interface, Windows/macOS and a Python 3.10 interpreter were not available for this verification. The smoke test establishes extracted-package helper operation, not universal agent compliance with task lifecycle or authority instructions. Upstream's historical behavioral limitations remain recorded in the adjacent verification documents.

`style-init --check` reported missing `.editorconfig` and `ruff.toml`. Both `style-check --fix` and `style-check` ran on the changed source files and skipped Python/Markdown because this repository has no corresponding configuration. No formatter, dependency, hook configuration, remote or installed Cowork skill was changed.
