# Fit the Cowork workspace to its owner

Claude Cowork is the sole supported end-user app. Read installed memory-setup’s tracking-model instructions before filing old notes. The staged Release is setup material, not a skill-source tree to copy into the workspace.

Follow staged `README.md`, "Guide the owner at every step", throughout adaptation. Give the next concrete action when owner input is needed and verify its result before continuing. Keep routine path discovery, file operations and checks with the agent. Personalization remains a conversation about the owner’s work, not a questionnaire about technical tools.

## 1. Verify installation and access

Confirm the owner saved the selected ready-made `.skill` cards into Cowork and attached the workspace. Locate the actual installed personal-memory package in this session; verify its task templates, supporting templates, scaffold and helper scripts. Do not assume a path, create a workspace source copy or claim installation from the presence of source files. If workspace access is missing, say: “Click **Add folder**, select your workspace folder and confirm, then tell me when it is attached.” Use **Choose folder** if that is the visible picker label. For installed-skill access, explain which saved card or permission is missing; do not ask the owner to guess an installation path. Use only documented manual checks where permitted.

For an optional Git repository with Python, verify the installed helpers before configuring local `cowork.personalMemoryPath` and `.githooks`. The machine-local path can change across sessions; missing helpers must be reported, never silently skip an audit. Without Python, disclose that only the message-length hook is available.

## 2. Settle the owner’s organization

Use installed memory-setup and personal-memory to recommend from the work the owner actually does; preserve the owner's existing organization unless a change is agreed. Treat the layouts below as starting points, not a requirement to organize every workspace alike. Ask only decision-changing questions. Independent work uses `projects/<short>/README.md` and useful folders; client work can retain `clients/` alongside projects. No fictional projects, facts or verified procedures are needed to complete an empty scaffold.

Set the folder map and schema together with approval. Preserve existing `client_folder`, subjects, `client_dirs` including an empty list, topics and topic directories during updates; proposed additions need approval. Verify real project/file links when available. Use installed personal-memory’s task and supporting templates. Keep one root `tasks/index.md` linking active/waiting records in `projects/<subject>/tasks/` or `clients/<client>/tasks/`, or other task homes agreed in the folder map. Root `tasks/` supports unassigned and legacy work. Do not move existing tasks or remove existing indexes without approval. Use tasks.md for discovery, progress, recovery and archival across these homes; memory holds lasting facts, not duplicate task status.

## 3. Learn the owner’s environment

Ask what the owner works in day to day: apps, accounts, connected services, shared folders and the files they reach for most. Check what this Cowork session can actually reach (attached folders, connectors) and say plainly what works now and what needs a folder attached or a connector added. Save approved durable facts through installed personal-memory as the owner’s own note, such as `memory/preferences/tools-and-accounts.md`, loaded by adding it to Also load on the existing “Using a tool, connector or workstation setup” row in `memory/rules.md`, keeping that row’s workflow-index pointer. This note is the owner’s, separate from the shipped Cowork environment preference. Done when the owner has confirmed the list and each item is marked reachable, needs access, or out of scope.

## 4. Practice on real work

Adaptation is finished by doing. Run up to four short practice runs on the owner’s real material, choosing those that fit their work:

1. **A project or tracked thing:** set up one real project README or tracked subject with its actual files and links.
2. **A saved task:** save one piece of real unfinished work. After a migration, pick up a migrated task instead.
3. **A recurring job:** do one job the owner repeats, such as an email draft, research or a report, end to end with them. Choose a meeting transcript only after the installed meeting skill has a working helper route for this workspace.
4. **A procedure:** when that job repeats, offer to draft it as a procedure. The practice run counts as its verification only if the owner watched it work; save it only on their approval.

Before each run, say in one line what it will show them. After each, ask: “What would you change about how that went?” Turn answers and corrections into proposed preferences for section 5. Done when each chosen run is finished or the owner skipped it. When the owner wants to stop early, offer to save one saved task, “Finish adapting the workspace”. The staged guides are not in the workspace, so the task itself carries what a later session needs: the Release name, the stages done, each remaining practice run with one line on what it covers, preferences proposed but not yet saved, cards not yet installed, and the remaining steps (section 5, then README First setup steps 5-7: remaining skills, suggested rules, finish). Its next action names the next run. On explicit pickup, run the remaining practice, then ask the owner to attach the Release ZIP again for the remaining steps, or finish them from the task’s list when it is unavailable and say so.

## 5. Personalize behavior

Start from what practice showed: propose preferences from the owner’s answers and corrections during the runs. Then discuss only other choices relevant to this owner’s work, such as answer style, document destinations or recurring work; skip settled or irrelevant topics rather than run an exhaustive checklist. Save approved preferences through installed personal-memory, with rule rows pointing to the relevant notes. Preserve previous handwritten memory before edits. Do not put personal rules into shipped `CLAUDE.md` or edit packaged skills as a substitute for a preference.

Optional video skills and any start-of-day routine are separate choices. For meetings, use the installed meeting skill’s first-use instructions and verify a real run; until it resolves its script from the installed package, use its without-Python route and say so. For a routine or memory sweep, use Cowork only; do not prescribe another app, external headless command or a scheduler that cannot reach this workspace. Report untested scheduling as untested.

## Updates preserve owner content

Updates use an attached ZIP and a verified backup, retain the same workspace path, and replace only approved projected user files. Skill cards are presented from staging and saved into Cowork, not copied as source or archives into the workspace. Keep the package index for future comparisons. Existing custom skills and legacy source trees stay untouched unless the owner explicitly approves a scoped cleanup. Plain CRLF/LF differences are not personal edits or separate approval decisions.

Verify installed helpers, memory/tasks/project links, preservation of owner content and the optional Git hook before reporting completion. Separate checked behavior from native Cowork actions still needing the owner.
