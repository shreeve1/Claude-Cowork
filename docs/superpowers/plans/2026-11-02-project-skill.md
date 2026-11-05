# Project Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a core Cowork skill, `project`, that opens any project with a briefing, imports Claude app Projects by sorted, owner-approved import, and creates owner-approved per-project skills inside Cowork; wire it into setup, migration, updates and routing.

**Architecture:** Markdown-only skill in `.claude/skills/project/` with three files split by branch: `SKILL.md` (home resolution + Open), `import.md`, `project-skills.md`. Layout tests pin structure and the decisions the spec fixes; packaging reuses `cowork_skills.py`; behaviour is proven with scripted scenario runs in scratch workspaces, then on James's desktop.

**Tech Stack:** Markdown skills; Python 3.10+ stdlib `unittest` for layout tests; existing `cowork_skills.py` build; personal-memory helpers.

**Spec:** `docs/superpowers/specs/2026-11-02-project-skill-design.md`

## Global Constraints

- Claude Cowork only. Tool names as shipped: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `present_files`, `AskUserQuestion` (not used where a skill says ask in plain text).
- No new scripts or dependencies in the skill. Tests use stdlib only.
- Skill frontmatter keys only from `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`; description at most 1024 characters, no `<` or `>`; name kebab-case matching the folder (`cowork_skills.check`).
- Never assume client or project: homes come from `memory/schema.json` (`client_folder`, `client_dirs`) and `memory/preferences/document-scaffolding.md`; speak the owner's word.
- Imported instructions are evidence until the owner approves them; workspace and safety rules win on conflict.
- Credentials never cross into files or memory; report by source line, never value.
- Memory writes go through installed personal-memory with its recovery protocol; import never changes `memory/schema.json` or the folder map without separate owner approval.
- Re-import never overwrites: proposal shows differences only; removed source files are reported, not deleted.
- Project skills: only with per-project owner approval; hold steps only, no facts; source at `<home>/<short>/skill/SKILL.md`; installed via `.skill` + `present_files` + **Save skill**.
- Daily work never depends on setup staging or the maintainer source tree.
- Before committing a change to a skill script (`cowork_skills.py`), a `reviewer` agent reviews the diff against `CODING_STANDARDS.md`.
- Commit exact paths only; subject `<area>: <what changed>`, at most 72 characters.

## Review Focus

1. **Two homes with the same short name** (`projects/openly/` and `clients/openly/`): Open must ask, not pick the first. Pinned in Task 1 (`test_open_asks_on_multiple_matches`) and Task 5 scenario O2.
2. **Instructions that contradict workspace safety** ("always send without asking"): sorted as `covered`/`drop` with the conflict named, never adopted. Task 2 test + Task 5 scenario I3.
3. **A credential inside project instructions or docs**: excluded and reported by line. Task 2 test + Task 5 scenario I4.
4. **No project copy visible in the chat** (project not added, or folder not attached): stop with the exact clicks, fall back to paste/attach. Task 2 test + Task 5 scenario I5.
5. **Organisation blocks Save skill**: report blocked; project still works through the opener; no workaround. Task 3 test + Task 5 scenario S2.

---

### Task 1: Skill core and Open branch

**Files:**

- Create: `.claude/skills/project/SKILL.md`
- Create: `.claude/skills/project/tests/test_layout.py`

**Interfaces:**

- Produces: skill name `project`; section headings `## Find the home`, `## Open a project`, `## Import`, `## Project skills`; pointers `import.md`, `project-skills.md`; README line formats `Source: Claude Project <id>, imported YYYY-MM-DD` and `Skill: <name>` (inside the Project README Files section).

- [x] **Step 1: Write failing layout tests** in `tests/test_layout.py` (pattern: `.claude/skills/memory-setup/tests/test_layout.py`):
  - `test_frontmatter`: name `project`; description contains `open`, `import`, `Claude` and `skill`; `cowork_skills.check(SKILL)` returns `[]` (import via `sys.path` from `.claude/cowork`).
  - `test_every_reference_linked`: the set of `*.md` besides `SKILL.md` equals `{"import.md", "project-skills.md"}` and each name appears in `SKILL.md`.
  - `test_home_from_schema`: `SKILL.md` names `memory/schema.json`, `client_folder` and `memory/preferences/document-scaffolding.md`, and never contains `clients/` (homes come from the schema, not a fixed word).
  - `test_open_loads_every_link`: Open section names `README.md`, `instructions.md`, `tasks/index.md`, and the phrase `opened or reported missing`.
  - `test_open_asks_on_multiple_matches`: Open section contains `several` and `ask which`.
  - `test_instructions_scoped`: contains `safety rules win` and `Switching projects`.
  - `test_brief_names_project_skill`: Open section contains `Skill:` (the README line) and says to name the skill in the briefing.
  - `test_personal_memory_paths_exist`: copy memory-setup's check so every `personal-memory/<file>` reference exists.
- [x] **Step 2:** Run `python3 -m unittest discover -s .claude/skills/project/tests -v`. Expected: FAIL (missing `SKILL.md`).
- [x] **Step 3: Write `SKILL.md`** following writing-for-agents: description is the spec draft (front-loaded leading word `Project`, one trigger per branch). Body: Find the home (spec "Home resolution"), Open steps 1-4 with the spec's completion criterion and ~150-word briefing fields, one-line pointers to `import.md` and `project-skills.md`, and personal-memory resolution as memory-setup step 2 words it (installed package, never a fixed path; if absent, ask for the ZIP and present `personal-memory.skill`).
- [x] **Step 4:** Re-run the tests. Expected: PASS.
- [x] **Step 5: Commit** `git add .claude/skills/project/SKILL.md .claude/skills/project/tests/test_layout.py` then `git commit -m "project: add skill core and open branch"`.

### Task 2: Import branch

**Files:**

- Create: `.claude/skills/project/import.md`
- Modify: `.claude/skills/project/tests/test_layout.py`

**Interfaces:**

- Consumes: Task 1 headings and README line formats.
- Produces: verdict words `project`, `owner-wide`, `covered`, `drop` (used by Task 5 checks).

- [x] **Step 1: Add failing tests** for `import.md`:
  - `test_reads_cowork_project_copy`: names `metadata.json`, `memory.md`, `docs/`, `files/`, and `Add folder`.
  - `test_four_verdicts`: each of `` `project` ``, `` `owner-wide` ``, `` `covered` ``, `` `drop` `` appears.
  - `test_approval_before_write`: text `Write nothing until` precedes the write step.
  - `test_reimport_never_overwrites`: contains `Source:` and `differences`, and `not deleted`.
  - `test_files_limits_named`: contains `Word`, `text only`, `ID`, and `git-ignored`.
  - `test_credentials_by_line`: contains `by line` and `never value`.
  - `test_no_copy_visible_fallback`: contains `paste` and the exact clicks to add the project and folder.
  - `test_batch`: contains `one project per chat` and a reported done list from `Source:` lines.
  - `test_ends_with_open_as_proof`: last numbered step names the Open branch.
- [x] **Step 2:** Run tests. Expected: FAIL.
- [x] **Step 3: Write `import.md`**: the spec's Import steps 1-8 plus the builder-check calls (re-import differences, raw copy never lands in the workspace, lasting facts per tracking model, client-owned path `<client_folder>/<client>/projects/<short>/`). Step 6 points to `project-skills.md` when steps exist. Proposal message lists per project: home, short name, instruction verdicts, memory notes, file notes, skill recommendation.
- [x] **Step 4:** Run tests. Expected: PASS.
- [x] **Step 5: Commit** `project: add sorted Claude Project import`.

### Task 3: Project skills inside Cowork

**Files:**

- Create: `.claude/skills/project/project-skills.md`
- Modify: `.claude/skills/project/tests/test_layout.py`

**Interfaces:**

- Consumes: `cowork_skills.check(folder) -> list[str]` and `cowork_skills.package(folder, dest)` as the reference format (the skill describes the same layout in prose; Cowork has no access to the maintainer script).
- Produces: project skill template (frontmatter + `Open the project first` line + Steps section) embedded in `project-skills.md`.

- [x] **Step 1: Add failing tests**:
  - `test_template_passes_cowork_checks`: extract the fenced template from `project-skills.md`, fill `name: openly-design` and a sample description, write to a temp `openly-design/SKILL.md`, assert `cowork_skills.check(...) == []`; package with `cowork_skills.package` and assert the zip lists exactly `openly-design/SKILL.md`.
  - `test_steps_only_no_facts`: text says the skill holds steps and points to `README.md` for facts.
  - `test_requires_owner_approval_and_save_skill`: contains `approval`, `present_files`, `Save skill`.
  - `test_blocked_install_reported`: contains `forbids` (or `blocked`) and `opener`.
  - `test_name_collision_checked`: contains `installed` and `shipped` skill names.
- [x] **Step 2:** Run tests. Expected: FAIL.
- [x] **Step 3: Write `project-skills.md`**: when to recommend (repeatable steps, not reference); source path `<home>/<short>/skill/SKILL.md`; package as a zip with `<name>/SKILL.md` at the root into session outputs (Python `zipfile` in the sandbox, or Cowork's skill-creator if installed); the upload rules list from Global Constraints; `present_files`; owner clicks **Save skill**; verify availability; update = edit source, repackage, save again; blocked install path. Add the README `Skill:` line.
- [x] **Step 4:** Run tests. Expected: PASS.
- [x] **Step 5:** Review `SKILL.md`, `import.md` and `project-skills.md` together against the writing-for-agents skill; fix findings and re-run Tasks 1-3 tests.
- [x] **Step 6: Commit** `project: add owner-approved project skill creation`.

### Task 4: Wiring, packaging and routing

**Files:**

- Modify: `.claude/cowork/workspace/rules.md` (row "Starting or continuing work on a project")
- Modify: `memory/rules.md` (same row; personal-memory recovery snapshot first)
- Modify: `.claude/setup/README.md` (First setup: new step 7 "Offer project import" before **Finish**, which becomes step 8; "Skills in Cowork" exception paragraph; Update step 5: switch the project rules row only after the `project` card is confirmed installed, else keep today's row)
- Modify: `.claude/cowork/cowork_skills.py` (`CORE` gains `"project"`)
- Modify: `.claude/skills/convert-release/tests/test_cowork_workspace.py` (new assertions)
- Generated: `.claude/cowork/skills/core/project.skill`, `.claude/cowork/skills/index.json`, `MANIFEST.json`
- Modify: `CHANGELOG.md`

**Interfaces:**

- Consumes: skill name `project`.
- Produces: rules row `| Starting or continuing work on a project | skill \`project\` | \`memory/preferences/document-scaffolding.md\` | Open the project and brief before work. |`

- [x] **Step 1: Add failing tests** in `test_cowork_workspace.py`:
  - `test_setup_offers_project_import_before_finish`: in `.claude/setup/README.md`, the first-setup step mentioning `project` import appears before `**Finish.**`.
  - `test_setup_documents_project_skill_exception`: "Skills in Cowork" contains `project-skills.md` and `Save skill`.
  - `test_update_switches_project_row_after_install`: update step 5 contains `project` and `confirmed`.
  - Existing `test_first_stage_installs_every_rule_skill...` will fail until `project.skill` exists, which pins packaging.
- [x] **Step 2:** Run `python3 -m unittest discover -s .claude/skills/convert-release/tests -v`. Expected: the three new tests FAIL.
- [x] **Step 3:** Edit the shipped rules row and setup README. Snapshot `memory/rules.md` with `python3 .claude/skills/personal-memory/recovery.py --root . snapshot memory/rules.md`, re-read, then change its row the same way.
- [x] **Step 4:** Add `"project"` to `CORE`; run `python3 .claude/cowork/cowork_skills.py build`. Expected: exit 0, `project.skill` written, manifest refreshed; check printed modes.
- [x] **Step 5:** Add a first bullet under "Cowork-only changes:" in `CHANGELOG.md`: the new `project` skill (open, sorted import, owner-approved project skills), the setup step and the rule exception; say native Cowork run is pending until Task 6. (`memory/preferences/cowork-environment.md` already records the exception, commit `e8289b2`.)
- [x] **Step 6:** Run all suites: `for d in .claude/skills/*/tests .githooks/tests; do python3 -m unittest discover -s $d; done` and `python3 .claude/skills/personal-memory/gate.py --memory memory audit`. Expected: all pass. Delete `__pycache__/`.
- [x] **Step 7:** `reviewer` agent reviews the `cowork_skills.py` diff against `CODING_STANDARDS.md`; fix findings.
- [x] **Step 8: Commit** exact paths: `cowork: ship project skill and wire setup routing`.

### Task 5: Scenario runs in scratch workspaces

**Files:**

- Create: `docs/testing/project-skill-cases.md` (cases, runs, results)

**Interfaces:**

- Consumes: installed-style copy of `project.skill` and `personal-memory.skill` extracted to a temp folder; scratch workspaces from `workspace.py create`.

- [x] **Step 1: Build fixtures**: (a) project-only workspace (`client_folder: projects`); (b) client workspace with `projects/` too; (c) custom word (`campaigns`). Fake Cowork project copy from the Openly design export shape (`metadata.json`, `memory.md`, `docs/` incl. a Word-as-text file, `files/` with ID names), plus a variant with a credential line and a safety-contradicting instruction.
- [x] **Step 2: Run each case with a fresh `cheap` subagent** given only the installed skill and the scenario prompt; record the agent's proposal/briefing and files written:
  - O1 one match → briefing within ~150 words with all fields; O2 same short name in two homes → asks; O3 no match → lists and offers import; O4 switch projects → drops old instructions.
  - I1 import into each fixture → correct home, approval before writes, README `Source:`; I2 re-import → differences only; I3 contradicting instruction → not adopted; I4 credential → by line only; I5 no copy visible → exact clicks.
  - S1 project with repeatable steps → recommends skill, `.skill` passes `cowork_skills.check`; S2 blocked Save skill → reported, opener still works.
- [x] **Step 3:** Fix skill text for any failure; re-run only failed cases; re-run Tasks 1-3 tests and rebuild.
- [x] **Step 4: Commit** `docs/testing/project-skill-cases.md` and any skill fixes: `project: record scenario runs`.

### Task 6: Desktop acceptance (needs James's go-ahead for each UI action)

**Files:**

- Modify: `docs/testing/project-skill-cases.md` (acceptance section)

- [x] **Step 1:** Present `project.skill` in Cowork; James clicks **Save skill**; verify it is listed.
- [x] **Step 2:** New chat with Openly design + `itastack - Copy` attached; "import this project"; approve; verify files on disk against the project copy (checksums), README, memory notes, audit.
- [ ] **Step 3:** Fresh chat: "let's work on Openly design"; record the briefing.
- [x] **Step 4:** Create one project skill for a project with steps; James clicks **Save skill**; trigger it in a fresh chat.
- [ ] **Step 5:** Try two projects in one chat; record whether both copies are visible (spec's open question).
- [x] **Step 6:** Record results; list cleanup items (test chats, test folders, test skill) and remove only what James approves. Commit `project: record desktop acceptance`.
