# Fit the Cowork workspace to its owner

Claude Cowork is the sole supported end-user app. Read installed memory-setup’s tracking-model instructions before filing old notes. The staged Release is setup material, not a skill-source tree to copy into the workspace.

Follow staged `README.md`, "Guide the owner at every step", throughout adaptation. Give the next concrete action when owner input is needed and verify its result before continuing. Keep routine path discovery, file operations and checks with the agent. Personalization remains a conversation about the owner’s work, not a questionnaire about technical tools.

## 1. Verify installation and access

Confirm the owner saved the selected ready-made `.skill` cards into Cowork and attached the workspace. Locate the actual installed personal-memory package in this session; verify its task templates, supporting templates, scaffold and helper scripts. Do not assume a path, create a workspace source copy or claim installation from the presence of source files. If workspace access is missing, say: “Click **Add folder**, select your workspace folder and confirm, then tell me when it is attached.” Use **Choose folder** if that is the visible picker label. For installed-skill access, explain which saved card or permission is missing; do not ask the owner to guess an installation path. Use only documented manual checks where permitted.

For an optional Git repository with Python, verify the installed helpers before configuring local `cowork.personalMemoryPath` and `.githooks`. The machine-local path can change across sessions; missing helpers must be reported, never silently skip an audit. Without Python, disclose that only the message-length hook is available.

## 2. Settle the owner’s organization

Use installed memory-setup and personal-memory to recommend from the work the owner actually does; preserve the owner's existing organization unless a change is agreed. Treat the layouts below as starting points, not a requirement to organize every workspace alike. Ask only decision-changing questions. Independent work uses `projects/<short>/README.md` and useful folders; client work can retain `clients/` alongside projects. No fictional projects, facts or verified procedures are needed to complete an empty scaffold.

Set the folder map and schema together with approval. Preserve existing `client_folder`, subjects, `client_dirs` including an empty list, topics and topic directories during updates; proposed additions need approval. Verify real project/file links when available. Use installed personal-memory’s task and supporting templates. Keep one root `tasks/index.md` linking active/waiting records in `projects/<subject>/tasks/` or `clients/<client>/tasks/`, or other task homes agreed in the folder map. Root `tasks/` supports unassigned and legacy work. Do not move existing tasks or remove existing indexes without approval. Use tasks.md for discovery, progress, recovery and archival across these homes; memory holds lasting facts, not duplicate task status.

## 3. Personalize behavior

Discuss only choices relevant to this owner’s work, such as answer style, document destinations or recurring work; skip settled or irrelevant topics rather than run an exhaustive checklist. Save approved preferences through installed personal-memory, with rule rows pointing to the relevant notes. Preserve previous handwritten memory before edits. Do not put personal rules into shipped `CLAUDE.md` or edit packaged skills as a substitute for a preference.

Optional video skills and any start-of-day routine are separate choices. For meetings, use the installed meeting skill’s first-use instructions and verify a real run. For a routine or memory sweep, use Cowork only; do not prescribe another app, external headless command or a scheduler that cannot reach this workspace. Report untested scheduling as untested.

## Updates preserve owner content

Updates use an attached ZIP and a verified backup, retain the same workspace path, and replace only approved projected user files. Skill cards are presented from staging and saved into Cowork, not copied as source or archives into the workspace. Keep the package index for future comparisons. Existing custom skills and legacy source trees stay untouched unless the owner explicitly approves a scoped cleanup. Plain CRLF/LF differences are not personal edits or separate approval decisions.

Verify installed helpers, memory/tasks/project links, preservation of owner content and the optional Git hook before reporting completion. Separate checked behavior from native Cowork actions still needing the owner.
