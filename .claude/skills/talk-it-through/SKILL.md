---
name: talk-it-through
description: |
  Stress-test a plan or process against the team's shared language and previously recorded decisions, sharpen fuzzy terminology, maintain a CONTEXT.md glossary inline, and automatically record what was settled.

  Use when the user wants to pressure-test a plan, workflow, or document, sense-check a decision, or mentions "talk it through".
---


# Talk It Through

## Workflow

Reach a shared understanding of this plan, process, or document by settling the vital few decisions and defaulting the rest. The vital few are hard to reverse, have other decisions hanging off them, or are expensive or embarrassing to get wrong. Everything else gets a stated default.

Each turn:

1. **Explore first.** Re-read the files, memory and documents this turn depends on; form claims from them, never from earlier turns. A fact the workspace or a web search can answer is yours to find, never a question. Send a subagent for slow lookups and ask only what does not wait on it.
2. **Diagram.** Show the plan as you understand it in a Mermaid flowchart. Redraw it whenever an answer changes its shape.
3. **Defaults.** A numbered table (D1, D2, …) of every low-stakes call you made for the user, one line each.
4. **Questions.** At most 3 vital questions, in dependency order; a question whose answer depends on another waits for the next turn. Format each as plain chat text:

   ```
   ❓ **Q1 - <title>**: <question, with the options>

   ➡️ <recommended answer>
   ```

5. **Reply handling.** "ok" accepts every recommendation and default. "Q2: no, D4: weekly" overrides only those.

Never use the `AskUserQuestion` tool. Stop when no vital question remains: say so, show the final diagram and defaults table, then wrap up.

## Supporting Information

### Awareness of existing language and decisions

At the start of a session, look for what's already been decided so you can challenge against it:

- A `CONTEXT.md` at the workspace root — canonical vocabulary: contested/overloaded terms with a chosen form and aliases to avoid ("which meaning?"). See [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).
- `memory/glossary.md` — the entity directory: shorthand -> full identity ("who/what is this?"). CONTEXT.md and glossary.md are siblings — keep contested vocabulary in CONTEXT.md and plain label expansions in glossary.md.
- `memory/index.md` — read the whole Promoted Memory table. This is the discoverability map for everything in memory, not just decisions: preferences, workflows, docs, and decisions all appear here (workflows and decisions through the generated sub-indexes `memory/workflows/index.md` and `memory/decisions/index.md`, linked from the table).

Read the index up front, but pull full memory files lazily: open a specific entry (for example a row under `memory/preferences/`, `memory/docs/`, or a file listed in the workflow/decision sub-indexes) only when its summary looks like it might inform or contradict the topic being discussed. Don't eagerly read the whole memory tree every session. See [DECISIONS-FORMAT.md](./DECISIONS-FORMAT.md) for decision specifics.

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. Use only the known sections from [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md); do not invent unresolved terms, relationships, or example dialogue just to fill the file.

### During the session

#### Challenge against the glossary

When the user uses a term that conflicts with the agreed language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'client' as a billing entity, but you seem to mean the day-to-day contact — which is it?"

#### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'sign-off' — do you mean the manager's approval or the client's acceptance? Those are different gates."

#### Discuss concrete scenarios

When relationships between people, steps, or documents are being discussed, stress-test them with specific scenarios. Invent realistic situations that probe edge cases and force the user to be precise about who does what, in what order, and what happens when something is missing.

#### Cross-reference with what's recorded

When the user states how something works, check whether the recorded memory or the referenced document agrees. If you find a contradiction, surface it: "Last month you decided invoices go out on the 1st, but you just said month-end — which is right?"

#### Maintain CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` is a glossary of agreed terms and relationships — nothing else. Keep it free of step-by-step procedure, task lists, or decision rationale. Those belong in the document being discussed or in a memory decision. Plain shorthand -> identity expansions belong in `memory/glossary.md`, not here.

Leave sections absent until they have real content. For example, do not add `Example dialogue` until there is a useful real or synthesized exchange that clarifies the terms.

### Wrapping up — record what was settled automatically

This step is automated. Do **not** ask "do you want to record this?" A session wraps up when the user says to stop/wrap up, when you determine the remaining questions are low-stakes detail, or before you give the final summary.

A talk-it-through session is itself the approval: the user was actively in the loop settling things. So anything **clearly settled in-session** is promoted directly to its proper topic file. Anything you **inferred but the user did not explicitly confirm** is also written automatically per the CLAUDE.md capture rule, but mark it `unverified` in Notes. Do not ask first. There are no candidates.

#### 1. Identify what was settled, and route it by type

For each settled item, pick the type by what it is. When ambiguous, default to **decision**.

- **decision** — a choice about what gets done, who does it, or a process or boundary. → write to `memory/decisions/<topic>/decision-<slug>.md` per [DECISIONS-FORMAT.md](./DECISIONS-FORMAT.md).
- **preference** — how the user wants the assistant to behave or communicate. → merge into the closest existing file in `memory/preferences/`; a new file also gets a row in `memory/rules.md`.
- **rule** — "when X, use Y": a trigger that should load a skill or memory file. → a row in `memory/rules.md` per "Rules" in `.claude/skills/personal-memory/SKILL.md`.
- **voice** — a preference specific to voice-mode interaction. → merge into `memory/voice/voice-mode.md`.
- **workflow** — a repeated habit or sequence of steps. → merge into `memory/workflows/<topic>/`. Verified steps for one workflow are a Procedure, not a workflow note: a shared Procedure is written only through an owner-approved change, never auto-captured.
- **doc** — an important reference, link, or path to remember. → merge into the matching `memory/docs/<slug>.md` (one file per subject; create one only if none fits).
- **guide** — a reusable, redacted ticket-resolution note. Do NOT auto-write; Ticket Guides are saved only through an owner-approved change (one `ticket-guide` approval). Leave it for that flow.
- **glossary entity** — a shorthand -> identity mapping (client short name, nickname, acronym, codename). → merge into `memory/glossary.md`. Contested/overloaded terms instead go to `CONTEXT.md` inline, per above.

Pick the topic for a workflow or decision from the `topics` list in `memory/schema.json` (a new topic only with the owner's OK). After writing one, run `python3 .claude/skills/personal-memory/indexes.py` (regenerates the topic sub-indexes) and `gate.py audit`. 15-file rule: a memory folder holding more than 15 `.md` files directly gets topic subfolders plus a generated index; `gate.py crowded` reports it.

For decisions, follow [DECISIONS-FORMAT.md](./DECISIONS-FORMAT.md). For preferences, voice, workflows, and docs, follow [PROMOTED-MEMORY-FORMAT.md](./PROMOTED-MEMORY-FORMAT.md) — these merge into the owning topic file rather than creating one file per item. Both use the matching template in `memory/TEMPLATES.md` and write with `status: promoted`.

#### 2. Before writing, check for existing entries

Scan `memory/index.md` and the relevant topic folder for a matching entry. If one exists, overwrite it in place (bump `updated`) rather than creating a duplicate.

#### 3. Update the index and commit

Update `memory/index.md` (Promoted Memory table; workflows/decisions only need their sub-index, linked from `memory/index.md`). If updating an existing entry, update its existing index row date/summary instead of adding a duplicate. Run `python3 .claude/skills/personal-memory/indexes.py` and `gate.py audit` after writing, trim any file you touched this session that it warns about, then commit per "Commit at the end of every task" in `CLAUDE.md`.

#### 4. Tell the user

In one short line, say which items you recorded, their type, and where.

Skip an item only when it's purely transient (a one-off detail with no future relevance) or when it merely restates an existing recorded entry without changing it. If nothing qualifies, say so in one line.

Never store passwords, secrets, or other credentials in memory — omit them automatically and never ask. Client and third-party details (names, environments, contacts, config facts) are allowed in memory, except in Ticket Guides, which stay redacted per `memory/README.md`.
