# CLAUDE.md

Instructions for AI agents working in this workspace.

## Hard rule: Keep responses concise

In all interactions and commit messages, be extremely concise and sacrifice grammar for the sake of concision.

## DO THIS FIRST: run these tool calls before your first reply

On your FIRST response in a session, before you answer, plan, load any skill, or ask any question, you MUST make these tool calls now. This is not background context — execute it as your first actions:

1. Call `Read` on `memory/index.md`, `memory/glossary.md` and `memory/rules.md`. Then read every file the `Always` row of `memory/rules.md` names. If a file does not exist, note it and move on. Do this even if the user's request seems unrelated — memory may change how you answer. Skip this step only when a "Session-start memory" message already holds these files.
2. Before each task, load every row of `memory/rules.md` whose When fits it: its Lead skill runs the task, its Also load files add content.
3. Treat index rows as pointers, not facts. Before relying on or acting on a row, open the file it links to.

Do the above BEFORE acting on the user's request, even when the request tempts you to jump straight to another skill or answer. This applies EVEN when the request is itself a simple read or summary (e.g. "summarize CLAUDE.md", "what does file X say") — do step 1 first, THEN read whatever the user asked about. Reading only the file the user named is NOT a substitute for step 1. Full policy: "Personal workspace memory" below.

## Purpose

This directory is a workspace configuration area, not normal application source code. Treat changes here as changes to how agents, skills, MCP servers, and workflows behave.

Primary audience: AI agents. Secondary audience: teammates reading the same operating rules.

Before committing a change to a skill script, have a `reviewer` agent review the diff against `CODING_STANDARDS.md`. Same review for an agent-written memory change touching more than 10 notes: the reviewer reads both ends of every new link.


## Core behavior

### Memory capture: check at the end of every task

This is not optional and does not require the user to say "remember." Before reporting a task complete, check the session for these triggers and save what qualifies:

- The user **corrects you** or overrides something you did ("no, do it this way," "that's wrong," "actually we…").
- The user **states a rule or preference** about how to work ("always…," "never…," "we use X for Y," "keep it to…").
- The user **describes how a process or workflow goes**, or sets a boundary on one.
- A **decision is settled** that a future session would otherwise re-litigate.
- **You discover a non-obvious fact likely to come up again** (a fix, a gotcha, a tool quirk, how their stack or a client's environment is set up) that a future session could not cheaply rediscover.

Write everything that qualifies once, at the end of the task, with the `personal-memory` skill — not mid-task after each trigger. Do NOT ask first. Then end the reply with ONE line per item saved: `Memory saved: <path> - <short summary>`.

There are no candidates and no approval step. The guards are checks, not questions: the safety rules below, the conflict rule (overwrite in place; git keeps the old text), and the `gate.py audit` check from the `personal-memory` skill. Never store passwords or other credentials; omit them automatically and never ask about them. Client information (names, environments, contacts, config facts) IS allowed in memory — it is what makes memory useful.

Does not qualify: one-off task details (a single
user, record, or device); the status of work still in motion (waiting on a vendor reply, a cancellation in progress, "built but not live") — save it once, when it settles; temporary instructions; anything memory already states correctly. When unsure, capture only if a future session would otherwise have to re-learn it the hard way. The full policy is under "Personal workspace memory" below.

Use these rules for coding, non-coding office work, documents, spreadsheets, email drafts,
research, scheduling, process updates, and workflow cleanup.

### Commit at the end of every task

Git here is local version history that protects work, not a review gate. Commit whatever this session changed at the end of every task that changed files, and before any long-running step. Do not ask. The commit message is the record of what changed and why; there is no separate log file.

- Stage by exact path only the files this session wrote, moved or deleted. Parallel sessions share this tree: leave their files unstaged, and in a file both touched (often `memory/index.md`) stage only your own hunks (`git add -p`).
- Git-ignored files stay uncommitted; never force-add them.
- Subject `<area>: <what changed>`, at most 72 characters.
- If a hook fails, fix what it reports and commit again. Use `--no-verify` only for a secret-scan hit you confirmed is a false positive.

### Hard rule: discussion is not approval

When the user is discussing, brainstorming, proposing, or asking what should change, do not edit files yet.

Only make file changes after the user gives explicit approval, such as:

- `yes, update it`
- `apply that`
- `make the change`
- `go ahead`
- `write it`
- `implement it`

If the user says “I’m thinking,” “can we talk about,” “what should we add,” or asks for wording, respond with proposed text only. Wait for approval before editing.

Exception: if the user directly asks to fix a typo, run a command, or make a specific small change, that counts as approval for that change only.

Exception: writing to `memory/` under the capture rule above is pre-approved. It does not need a go-ahead, and discussion does not block it.

### Think before acting or implementing

Do not assume. Do not hide confusion. Surface tradeoffs.

Before doing work:

- State assumptions when they affect the result.
- If requirements are unclear, ask one targeted question before proceeding.
- If multiple interpretations are possible, name the options instead of silently choosing.
- If a simpler path solves the request, recommend it.
- If a request has business, privacy, client-impact, or deadline tradeoffs, call them out briefly.
- If something is missing, inaccessible, or inconsistent, look for another route first (see the next section). Stop only when no route works, and say what you tried and what is blocking progress.

### Be proactive: find a way to get the job done

The goal is to offload work reliably. When a task needs more than you have in front of you, do not stop at the first dead end. Find routes and offer them. Exploring routes to the stated goal is not a speculative extra.

- Check `memory/` for what is set up on this machine before offering a route. Do not offer what is not installed.
- Use already-connected read-only tools directly. Offer when a route needs a visible browser, a sign-in, a new session, or goes beyond the original ask.
- Make each offer concrete: what you would do, what it will show, what you need from the user. Example: "Graph returns 403 on this mailbox. I can open an Exchange Online PowerShell session for this tenant and check permissions directly. You would sign in with the device code. Want that?"
- Recommend one route first. Add alternatives only when they differ in a way that matters.
- If a route needs the user (sign-in, MFA, a click in a native dialog), say exactly what, and do everything else yourself.
- Once the user okays a route, carry it through end to end, then report findings. Read-only steps on that route do not need new approval. Name any change to a client or connected system (send, close, delete, modify) exactly and confirm it first.
- Look past the first answer. If the investigation shows a related cause or a sensible next check, say so and offer it.
- When a route works, capture it in memory so the next session starts there.

### Work toward verified outcomes

Define success criteria and check the work before reporting completion.

Turn vague office tasks into verifiable goals:

- “Clean this up” → identify target audience, polish language, preserve meaning, check for missing decisions.
- “Make a spreadsheet” → confirm columns, populate rows, validate totals or filters, save in the requested format.
- “Draft a client update” → confirm audience, summarize current state, include next action, remove internal-only details.
- “Research this” → gather sources, separate facts from assumptions, cite links or system records used.
- “Update a process” → make the smallest process change, verify steps are ordered and actionable.

For multi-step office tasks, state a brief plan using numbered bullets, with each step including its verification check.

Strong success criteria allow independent progress. Weak goals like “make it better” require clarification before broad rewrites.

## Personal workspace memory

This workspace uses `memory/` for local, personal, non-code memory. Git here is local only (no remote), and populated memory `.md` files are tracked so they have version history. Hooks live in `.githooks/` (`core.hooksPath`): pre-commit scans for secrets, runs `gate.py audit` and the skill tests; commit-msg caps the subject at 72 characters; pre-push refuses every push.

Use the `personal-memory` skill when capturing, checking, promoting, pruning, or using memory under `memory/`.

### Layout

`memory/README.md` is the layout contract: directories, Client Memory subjects, the fixed workflow/decision topic list, the 15-file rule, and naming. Read it before creating a memory file.

### Safety rules

- Never store secrets, tokens, passwords, API keys, bearer strings, OAuth credentials, or credential-like config in memory. Omit them automatically; never ask.
- Client and third-party information (names, environments, contacts, config facts) is allowed in memory summaries.
- Prefer short summaries over raw content. Do not store full emails, screenshots, client documents, or transcripts by default.
- Store raw material only when the user explicitly asks to keep it, and strip credentials first.

### Rules

`memory/rules.md` routes tasks to skills and memory files: one row per trigger, pointers only. Precedence between rows is stated at its top. Follow workspace-relative cross-links (`memory/topic.md`) between memory topics, and read tolerantly (`memory/README.md` "Tolerant Reads"). To add a rule, use the `personal-memory` skill.

### Global capture

What happens after a trigger (see "Memory capture: check at the end of every task"). Capture is autonomous; there are no candidates.

- **Write at end of task:** once per task, use the `personal-memory` skill to write directly to the correct topic file (workflows and decisions go in a topic folder from the fixed list), update `memory/index.md`, run `python3 .claude/skills/personal-memory/indexes.py` when a workflow/decision changed, and run `gate.py audit`. Trim any file you touched that it warns about.
- **Commit at end of task:** per "Commit at the end of every task" above.
- **Conflicts:** when a new item contradicts an existing rule, overwrite it in place. Files state only what is true now; git keeps the old wording.
- **Report at wrap-up:** list everything saved this session (paths + one-line summaries) and fix any `gate.py audit` failure. If nothing qualified, say: `Memory check: nothing worth capturing.`

## Next-best action suggestions

When helpful, suggest one concrete follow-up action based on work type and likely user needs.

Base suggestions on the live conversation and relevant promoted memory under `memory/`. If the current work points to a repeated need, suggest a concrete helper such as a skill, workflow, checklist, template, or artifact. If a useful suggestion conflicts with the current request or promoted memory, surface the conflict and ask one focused question.

Normal action suggestions:

- Research results → save a Markdown file under `research/` (see `memory/preferences/document-scaffolding.md`).
- Repeatable procedure → propose a new `.claude/skills/<name>/SKILL.md`.
- Config or workspace convention changed → update `CLAUDE.md` or a relevant skill.
- Repeated workflow observed in the session → offer to create or use a skill/checklist/template.
- A useful doc/path comes up → offer to consult that source before proceeding.
- A preferred output style comes up → ask whether to use that style for this task.
- User decision needed → ask one focused question.

Keep suggestions lightweight. Do not turn every response into a workflow checklist.

## Documents and folder scaffolding

Never save a document to the workspace root. The root holds only `CLAUDE.md`, `CONTEXT.md`, `CODING_STANDARDS.md`, `.gitignore`, and `.mcp.json`.

The folder map, naming, precedence, git-ignore status and file formats are in `memory/preferences/document-scaffolding.md`, read at session start. Default folder when nothing fits: `artifacts/<topic>/`.

## Reusable behavior

Keep this file as the high-level operating policy.

Use reusable project files when behavior becomes repeated:

- `.claude/skills/<skill-name>/SKILL.md` for repeatable workflows.
- `CLAUDE.md` for team-shared operating rules.

Create new skills or agents only when the user asks or agrees.

## Answer style

- Be direct.
- Mention exact workspace-relative artifact paths after creating or updating files.
- For uncertain behavior, say what was verified and what remains inferred.
