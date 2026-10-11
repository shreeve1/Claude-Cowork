# Personal Memory Reference

Rare operations for the `personal-memory` skill: setting up the system, recovering missing scaffold, and linting memory health. `SKILL.md` covers everyday capture and reads; open this file only for one of these three.

## Setup Workflow

Use when setting up this memory system in a workspace.

1. Create directories:
   - `memory/preferences/`
   - `memory/docs/`
   - `memory/voice/`
   - `memory/email/`
   - `memory/guides/`
   - `memory/workflows/<topic>/` and `memory/decisions/<topic>/` — one folder per topic in the `topics` list of `memory/schema.json` (a new topic only with the owner's OK)
   - `memory/<client_folder>/` (`clients` unless `memory/schema.json` sets `client_folder`)
   - `memory/raw/`
2. Create committed scaffold files if missing:
   - `memory/README.md`
   - `memory/TEMPLATES.md`
   - `.gitkeep` in each memory subdirectory.
3. Add or update `.gitignore` so `memory/raw/` and binaries are ignored while memory `.md` files are tracked; make sure the repo has no remote and a pre-push hook refuses pushes.
4. Add or update `CLAUDE.md` with the personal memory rules.
5. Do not create a populated `memory/index.md` until the first capture or promotion.
6. Verify paths exist and report changed files.

## Recovery Workflow

Scaffold or personal files may be missing in a fresh copy or teammate
workspace. Before writing any promoted memory in a run, ensure the scaffold
exists first, then recover the personal files:

- If `memory/README.md` or `memory/TEMPLATES.md` is missing, recreate it — it is
  scaffold, not personal state. Restore `README.md` as the memory
  contract and `TEMPLATES.md` as the canonical templates, using the shapes
  described in this skill and in the `talk-it-through` format docs
  (`DECISIONS-FORMAT.md`, `PROMOTED-MEMORY-FORMAT.md`, `CONTEXT-FORMAT.md`).
- If `memory/index.md` is missing, recreate it from the `TEMPLATES.md` index template before writing promoted memory.
- `memory/log.md` is retired. Never recreate it; the commit message is the log.
- If `TEMPLATES.md` is itself unavailable, do not block: fall back to the
  templates embedded in this skill and the format docs, and recreate
  `TEMPLATES.md` from them.
- Missing personal files are normal, not an error.

## Lint Workflow

Use when asked to review memory health or before broad cleanup.

Run the deterministic index audit first:

`python3 .claude/skills/personal-memory/gate.py --memory memory audit`

It reports promoted files missing from `memory/index.md`, index entries pointing to files that no longer exist, topic-folder problems (a promoted file directly in `workflows/`/`decisions/`, a topic folder not in `memory/schema.json`, a sub-index missing a file or drifted from `indexes.py`), and Client Memory problems (missing frontmatter keys, unknown subject, subject/client not matching the folders, note not on its hub, hub out of date, hub without an `index.md` row), and exits non-zero when anything needs fixing. It also prints `crowded` warnings (a memory folder holding more than 15 `.md` files directly) but does not fail on them. Fix hub problems by running `hubs.py`; fix sub-index drift by running `indexes.py`. `memory/candidates/` is not audited. For `gate.py audit` to recognize an index entry, the row must carry the file path either backticked (`` `memory/decisions/<topic>/decision-x.md` ``) or as a markdown link (`[title](memory/decisions/<topic>/decision-x.md)`).

Then also check for:

- Index rows pointing to missing files.
- Promoted files missing from `memory/index.md`.
- Empty promoted topic files.
- Conflicting active promoted rules.
- Cross-links pointing to memory files that do not exist (report only — broken links are tolerated, not auto-removed).

Report findings before making broad changes. Safe deterministic fixes include removing stale rows and adding missing index rows for existing files.

Note on `gate.py`: `audit` checks `memory/index.md` against the promoted files and Client Memory on disk, checks `memory/rules.md`, and prints lean-memory warnings (size, summary length, history lines, superseded files). `stale` lists notes not updated or verified in 90 days. It checks structure only; it does not check whether a memory item is true (see the grounding rule in Capture Workflow).

