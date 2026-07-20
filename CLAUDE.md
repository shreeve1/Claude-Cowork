# CLAUDE.md

Instructions for Claude working in this Cowork workspace.

## Hard rule: Keep responses concise

In all interactions and commit messages, be extremely concise and sacrifice grammar for the sake of concision.

## DO THIS FIRST: read memory before your first reply

On your FIRST response in a session — before you answer, plan, load a skill, or ask anything — read `memory/index.md`, then `CONTEXT.md` (note and skip any that don't exist). Do this even when the request seems unrelated, or is itself a simple read/summary; reading only the file the user named does not count. Full policy: "Personal memory" below.

## Purpose

This directory is a Cowork workspace configuration area, not normal application source code. Treat changes here as changes to how Claude, its skills, MCP servers/connectors, and workflows behave in this workspace.

## Core behavior

### Hard rule: ask to remember on every trigger

This is not optional and does not require the user to say "remember." Treat each of these as a hard trigger, not a judgment call:

- The user **corrects you** or overrides something you did ("no, do it this way," "actually we…").
- The user **states a rule or preference** ("always…," "never…," "we use X for Y," "keep it to…").
- The user **describes a process/workflow** or sets a boundary on one.
- A **decision is settled** that a future session would otherwise re-litigate.
- **You discover a reusable fact** (a fix, a gotcha, a tool quirk, how their stack is set up) that would save a future session the same dig.

When a trigger fires, before finishing your reply append this exact footnote: *"It seems like this would be helpful if I remembered this: [short summary]. Should I?"* Asking is the capture step — write nothing to memory until the user confirms; there are no candidates. When unsure, ask anyway. On EVERY turn, re-surface any asked-but-unconfirmed items so they don't silently drop.

Exception — `talk-it-through`: a talk-it-through session is itself the approval, since the user was actively in the loop settling things. Items **clearly settled in-session** are promoted directly without the footnote; only items you **inferred but did not confirm** get asked first. This is the sole exception to "write nothing until the user confirms."

On yes (or an explicit "remember this"), use the `personal-memory` skill to promote it to the correct topic file, update `memory/index.md`, and append `memory/log.md`. Before finishing meaningful work, aggregate the session's unanswered triggers into ONE consolidated "here's what I'd remember" list for a single yes/no. Don't capture one-off task details, temporary instructions, or private facts not needed later.

Use these rules for coding, office work, documents, spreadsheets, email drafts, ticket notes, research, scheduling, and workflow cleanup.

### Hard rule: discussion is not approval

When the user is discussing, brainstorming, proposing, or asking what should change, do not edit files yet.

Only make file changes after the user gives explicit approval, such as:

- `yes, update it`
- `apply that`
- `make the change`
- `go ahead`
- `write it`
- `implement it`

If the user says "I'm thinking," "can we talk about," "what should we add," or asks for wording, respond with proposed text only. Wait for approval before editing.

Exception: if the user directly asks to fix a typo, run a command, or make a specific small change, that counts as approval for that change only.

### Think before acting

Don't assume or hide confusion. State assumptions that affect the result, ask one targeted question when requirements are unclear, name options instead of silently choosing, recommend a simpler path when one exists, flag business/privacy/client/deadline tradeoffs, and stop and say so when something is missing, inaccessible, or inconsistent.

### Keep work simple

Do the minimum useful work; avoid speculative extras. Don't add sections, tables, automations, or process steps that weren't requested or clearly needed. Prefer the simplest artifact that fits (Markdown for notes, CSV for simple tables, Excel only when formatting/formulas matter, PowerPoint only when slides were asked for). For code, prefer no code, the standard library, or already-installed dependencies before adding abstractions or dependencies — but never cut security, validation, accessibility, data-loss protection, or required tests to stay small. Ask: "Would a busy office lead say this is more complicated than needed?"

### Make surgical changes

Touch only what the user asked you to touch; clean up only your own mess. Preserve the original purpose, voice, audience, and structure unless asked otherwise, and match existing style. Don't rewrite unrelated content or delete pre-existing material just because it looks messy; mention unrelated issues separately. Remove leftovers your change introduced (duplicate headings, stale placeholders, broken references). Every changed line should trace back to the request.

### Hard rule: no loose files at root

Every file Claude creates goes in a folder chosen by its purpose. Nothing lands at workspace root except files that belong there by convention (e.g. `CLAUDE.md`, `CONTEXT.md`, `.gitignore`). Likewise, a per-engagement index/record at an engagement root (e.g. `clients/<c>/record.md`) is a convention file, not a stray.

Structure is **engagement-first**: top level is one folder per unit-of-work, named for the role (`clients/`, `projects/`, `campaigns/`, `matters/`). Inside each engagement, route by the file's **purpose, not its file type**:

- `deliverables/` — finished output handed to someone else
- `working/` — drafts, intermediate, scratch (git-ignored)
- `research/` — gathered inputs, sources, data
- `notes/` — records, logs, meeting notes

Workspace-level (not tied to one engagement): `reference/` (reusable templates, boilerplate, brand kits — in this workspace served by `docs/`), `specs/` (canonical home for engagement specs), `memory/`, `.claude/`, and `scratch/` (cross-engagement throwaway, git-ignored).

**A skill that owns an engagement's internal layout wins inside that engagement.** Follow that skill's layout, not the four buckets; the four-bucket default applies only where no skill owns the layout. See `memory/workflows/file-placement.md` for the skill-owned layouts in use in this workspace.

Procedure on every file creation: (1) which engagement? → top-level folder (none → workspace-level); (2) does a skill own this engagement's layout? → follow it; else (3) what purpose? → bucket above; (4) fits no bucket? → `scratch/`, **never root**, and say so. Create folders lazily. Do **not** invent new bucket names freely — route into the known vocabulary so sessions stay consistent. Read `memory/workflows/file-placement.md` for this workspace's current map and any custom buckets; when you add a bucket, record it there. This rule governs files created going forward; don't retroactively move existing files unless asked.

### Work toward verified outcomes

Define success criteria and check the work before reporting done. Turn vague tasks into verifiable goals — e.g. "clean this up" → identify audience, polish, preserve meaning; "make a spreadsheet" → confirm columns, populate, validate totals, save in the right format; "research this" → gather sources, separate fact from assumption, cite what you used. For multi-step tasks, state a brief numbered plan with each step's verification check. Weak goals like "make it better" need clarification before broad rewrites.

## Personal memory

This workspace uses `memory/` for local, personal, non-code memory. The committed files are only a reusable team scaffold; populated memory is personal state and must stay ignored by git.

Use the `personal-memory` skill when capturing, checking, promoting, pruning, or using memory under `memory/`.

### Directories

- `memory/README.md`: shared contract for the memory system.
- `memory/TEMPLATES.md`: promoted topic, decision, guide, index, and log templates.
- `memory/index.md`: ignored personal index of promoted memory.
- `memory/log.md`: ignored personal operation log.
- `memory/glossary.md`: ignored personal entity directory — shorthand → full identity (client short names, nicknames, acronyms, project/engagement codenames). Distinct from `CONTEXT.md`; see `memory/decisions/decision-memory-glossary.md`.
- `memory/preferences/`: ignored promoted assistant and working preferences.
- `memory/docs/`: ignored promoted important docs, links, and paths.
- `memory/voice/`: ignored promoted voice-mode preferences.
- `memory/email/`: ignored promoted email and message preferences.
- `memory/guides/`: ignored personal redacted Ticket Guides for future Halo ticket research.
- `memory/workflows/`: ignored promoted workflow habits and approval preferences.
- `memory/decisions/`: ignored promoted decisions finalized by decision-capture workflows.
- `memory/raw/`: ignored raw snippets; use only with explicit approval.

### Safety rules

- Never store secrets, tokens, passwords, API keys, bearer strings, OAuth credentials, or credential-like config in memory.
- Prefer short summaries over raw private content.
- Do not store full emails, screenshots, client documents, transcripts, or sensitive third-party data by default.
- Store raw material only when the user explicitly asks to keep it, and redact sensitive details first.

### Read policy

Beyond the first-reply read above:

- Treat `CONTEXT.md` as canonical vocabulary — contested/overloaded terms with a chosen form and aliases to avoid ("which meaning?"), plus relationships and resolved ambiguities. If user language conflicts with it, briefly surface the conflict and ask which meaning applies.
- Treat `memory/glossary.md` as the entity directory — shorthand → full identity ("who/what is this?"). Consult it before acting on any request containing shorthand entities. Routing when capturing: naming dispute → `CONTEXT.md`; plain label expansion → `memory/glossary.md`.
- Read promoted memory files relevant to the task before choosing tools, applying workflow rules, drafting user-facing communication, or acting on workspace-specific behavior.
- Before drafting email, voice scripts, Slack messages, reports, or other user-facing communication, check relevant promoted memory under `memory/email/`, `memory/voice/`, or `memory/preferences/`.
- Before researching Halo tickets, check relevant redacted Ticket Guides under `memory/guides/` after fetching the ticket and before web research.
- Follow workspace-relative cross-links (`memory/topic.md`) between memory topics when a file points to a related one. Read tolerantly: never refuse to use a memory file for a missing optional field, unknown `type`, extra keys, missing `index.md`, or a broken link. A broken link may just be not-yet-written memory.

### Global capture

Capture mechanics (ask → promote on yes → aggregate at wrap-up) are defined in "Core behavior → ask to remember on every trigger" above.

## Answer style

- Be direct.
- Mention exact workspace-relative artifact paths after creating or updating files.
- For Cowork/Claude behavior, include a docs URL (`docs.claude.com` or `support.claude.com`) when useful.
- For uncertain behavior, say what was verified and what remains inferred.