---
name: talk-it-through
description: |
  Use when the user wants to explore, pressure-test, or decide on a plan, process, document, or ambiguous direction, especially when existing terminology, memory, or prior decisions matter.
---

# Talk It Through

Use this skill when the user wants help thinking something through before committing. It combines the superpowers brainstorming conversation shape with this workspace's vocabulary checks, decision cross-references, and memory capture.

## First: What Do You Actually Know?

Before replying, ask what is known about what the user wants and why.

- If everything important is in a quick, clear request, state any significant call and do it.
- If something material is missing, start the conversation instead of silently filling it in.
- Read relevant workspace files, memory, and existing decisions before relying on them. If a safe lookup can answer something, find it instead of asking the user.

## The First Message

For a non-trivial, underspecified request, the first message has two parts, in this order:

1. Tell the user they can ask you to skip the questions and start. If they do, brainstorming is complete: state significant implementation choices in one plain line and proceed through the normal workflow without the brainstorming approval gate.
2. Ask one open question that gets the user describing a real moment or concrete picture.

That is the whole first message. Do not add a questionnaire or process explanation. A specialized visual caller may add its direct link and brief visual context before this opening question; after that handoff, use the same single-question pattern.

If the user already supplied enough detail to make a recommendation, begin with the understanding and recommendation instead. Do not ask an opening question merely to follow a ritual.

## The Conversation

After the opening, build understanding through playback and recommendation rather than a question list.

- End each non-trivial conversation message with one question: a single sentence, with no list of example answers. When no material question remains, ask whether the user wants the recommendation acted on, then wrap up after their reply. Memory capture happens automatically and is not a question.
- Lead with what matters. Keep responses concise, plain, and idea-forward.
- Open questions come first when the user's intent is still unclear. Once a direction is clear, recommend a concrete path instead of asking the user to choose every detail.
- Ask only a question whose answer would materially change the direction, expose a costly risk, or clarify an unresolved term. Make low-stakes calls yourself and state them as your calls.
- When the user says “just guess” or “what do you think?”, propose something concrete.
- Match the user's vocabulary. Never make the user learn the workflow's process language.
- The builder-check questions that only the user can answer are brought in one message, even though ordinary conversation turns end with one question.

### How It Gets Made

Find out early which decisions about medium, tools, materials, resources, platform, programming language, or libraries the user wants to make and which they are handing to you. Build on existing work and say significant choices you make as your calls, not as choices the user agreed to.

### Ground to Cover

Use this as territory, not a script or checklist:

- what kind of thing this is and what makes it matter
- why the user cares and why now
- what success looks like
- goals, non-goals, and anti-goals
- what exists now and what has already been tried
- prior art the user has liked or disliked
- constraints, resources, and the details they care about
- what would make the result fail even if it technically worked

Questions that work anchor in specifics: “Walk me through the last time this happened,” “If it could only do one thing well, which would it be?” and “What would make you wince if I got it wrong?” A correctable guess is often better than a list of questions.

### Offer Recon

When looking would improve the conversation, offer to inspect the user's codebase or project, their own files and data, or the web. Say what you would look for. The user decides whether you go.

Use safe research practices. Do not send client-identifying details, private tickets, emails, internal hostnames, logs, or secrets to public search. Use connected read-only tools where available.

### Think Wide, Then Narrow

Before recommending a non-trivial direction, consider multiple distinct approaches and drop weak ones, including approaches that conflict with what the user said matters. Show comparisons only when they help the user decide.

Useful angles include:

- user or product experience
- technical system design
- workflow or operations
- adoption or business path
- adjacent-domain analogy
- contrarian or failure-mode perspective

Once one direction is clear enough to recommend, stop expanding.

### Play It Back

As soon as one part is understood well enough to describe, play it back in about 200 to 300 words, then return to the next unresolved part. State what the user said separately from what is inferred or guessed. Describe what the thing is for, who it serves, or how the relevant part behaves. If the playback describes something visual and the visual companion has not been offered, offer it in its own message and hold the playback until the user accepts or declines. End the playback with the one question that would change the direction or reveal what is missing.

When the user responds, update the playback and recommendation. Do not restart discovery or repeat settled questions.

## Show, Don't Tell

Offer something visual when seeing would help more than reading:

- a screen, page, printout, or sign
- a layout or arrangement
- a flow or sequence
- options that look different from one another
- a diagram, timeline, or map

Use a Mermaid diagram when it clarifies a flow, sequence, relationship, or decision path. In a talk-it-through session, once there is a truthful plan to show, open with that diagram and redraw it when the plan changes. For an underspecified first message, follow the first-message contract before drawing a diagram; do not invent a plan merely to satisfy the diagram preference. If a visual companion would help, offer it in its own short message:

> This might be easier if I show you. Want me to open a browser tab with some mockups?

If accepted and the picture is a flow, structure or map, use the `drawio` skill. Otherwise read `visual-companion.md` from the installed superpowers brainstorming skill, if there is one. If it is unavailable, stay in text and use Mermaid or a clearly labeled draft instead. Use the accepted companion for mockups, side-by-side options, or clickable throwaway prototypes when those will answer the question better than text. If the user declines, stay in text and do not offer the companion again unless they raise it.

## Spike to Learn

A quick throwaway experiment is often the cheapest way to learn whether an important direction works. Offer one when it would help. A spike may have minimal tests and skips the full plan, implementation, and review process. Keep it labeled temporary. Keeping or extending its output is a new request that returns through this conversation first.

## Size the Work

Once the direction is clear, name the size in plain language. The user can override it.

| Size | Full description | Next step |
|---|---|---|
| A quick, clear task | The request itself | Do it |
| A small change | The agreed direction in chat | Build through the normal workflow |
| A project with a written design | A document a builder can follow | Write and approve the design, then plan |

If the work grows, stop and say that it has crossed into the next size. If it is several independent projects, agree on an order and handle them one at a time.

## Written Design

For a project, write a plain design a capable builder can use without returning to the user. Cover:

- intent and why
- goals, non-goals, and anti-goals
- constraints
- decisions made during the conversation
- what remains for the builder to decide

Prepare the complete design text before writing it. In a software repository, the eventual path is `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` unless the user specifies another path. For other projects, ask where the design should go. After the user approves the complete design, write it, commit it if the project is a git repo, and then run the builder check.

When the user approves the complete design text, tell them that a reviewer will read it first and may return with a few questions. Read `builder-check-prompt.md` from the installed superpowers brainstorming skill directory. If it is unavailable, use this prompt: “Read the design and report only questions whose answers would change the implementation plan; skip details the builder can decide.” Dispatch a fresh general-purpose subagent with that prompt; if no subagent tool exists, read the design as the builder yourself. Sort the result into:

- answered by the conversation or project
- minor details a sensible builder can decide and mark as the agent's call
- questions only the user can answer because they change what gets built

Bring only the last group back to the user, most important first. This is the only question round produced by the builder check. Update the design with their answers and list the calls made for them to check. Do not hand over the design until this check is complete.

## Approval Before Building

Nothing is built until the user approves the full description for the chosen size:

- For a small change, approval is in chat.
- For a project, approval is of the complete design text before it is written; after approval, write the design (and commit it in a git repo), then run the builder check before implementation.
- Reading, inspecting, researching, and discussing are not building.
- A user-approved spike may be built as a throwaway experiment; keeping it is a new request.
- The opt-out in the first-message section and the approved spike are the only exceptions to this approval gate.

After the complete design text is approved and written, invoke `superpowers:writing-plans` and no other implementation skill when that skill is installed. If it is unavailable, write a plain numbered implementation plan in the approved design or a user-approved project document, state that substitution, and proceed from that plan.

## Existing Language and Decisions

At the start of a session, inspect the sources that may constrain the discussion:

- `CONTEXT.md` — canonical vocabulary for contested or overloaded terms. See [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).
- `memory/glossary.md` — shorthand to identity expansions.
- `memory/index.md` — the discoverability map for promoted memory, with workflow and decision sub-indexes.

Read the index up front, then open only entries that may inform or contradict the topic. Create files lazily. If no `CONTEXT.md` exists, prepare the proposed file contents when the first term is resolved, using only the known sections in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md), and write it only after the user explicitly approves the glossary change.

### Challenge the glossary

When a term conflicts with `CONTEXT.md`, call it out immediately and ask which meaning applies.

### Sharpen fuzzy language

When a term is vague or overloaded, propose a precise canonical term. Ask only if the distinction changes the recommendation.

### Stress-test concrete scenarios

When people, steps, or documents interact, use a realistic scenario only when it exposes a real edge case, missing owner, ordering problem, or failure condition.

### Cross-reference recorded decisions

When the user states how something works, check whether memory or the referenced document agrees. Surface contradictions instead of silently choosing between them.

### Maintain `CONTEXT.md` inline

When a term is resolved, prepare the proposed `CONTEXT.md` update during the session. Write it only after the user explicitly approves that glossary change. Keep it as a glossary of agreed terms and relationships, not a procedure, task list, or rationale record. Plain shorthand expansions belong in `memory/glossary.md`.

## Reply Shorthand

“ok” accepts the current recommendation and stated defaults. A targeted reply such as “Q1: no” or “use weekly instead” overrides only that point. Treat any correction as a new fact, update the playback, and continue from the revised understanding.

## Wrapping Up: Record What Was Settled

This step is automated. Do not ask whether to record settled information. A session wraps up when the user says to stop, when the recommendation is clear and no material question remains, or before the final summary.

For memory capture, the user's active participation is sufficient approval. This does not authorize building; the approval gate above still applies.

### Route each settled item by type

When ambiguous, default to a decision.

- **decision** — a choice about what gets done, who does it, or a process or boundary. Write to `memory/decisions/<topic>/decision-<slug>.md` per [DECISIONS-FORMAT.md](./DECISIONS-FORMAT.md).
- **preference** — how the user wants the assistant to behave or communicate. Merge into the closest file in `memory/preferences/`; a new file also gets a row in `memory/rules.md`.
- **rule** — “when X, use Y.” Add a row in `memory/rules.md` per the [personal-memory](../personal-memory/SKILL.md) rules.
- **voice** — a voice-mode preference. Merge into `memory/voice/voice-mode.md`; if that file does not exist, create it from the Promoted Topic File template and add its `memory/rules.md` route.
- **workflow** — a repeated habit or sequence. Merge into `memory/workflows/<topic>/`. A shared Procedure is written only through an owner-approved change.
- **doc** — an important reference, link, or path. Merge into the matching `memory/docs/<slug>.md`.
- **glossary entity** — shorthand to identity. Merge into `memory/glossary.md`; contested terms go to `CONTEXT.md`.

Choose workflow and decision topics from `memory/schema.json`. A new topic requires the user's approval. Never auto-write Ticket Guides. For preference, workflow, and doc shape and merge rules, read [PROMOTED-MEMORY-FORMAT.md](./PROMOTED-MEMORY-FORMAT.md) before writing.

### Before writing

Read `memory/index.md` and the relevant topic folder. Replace or merge an existing entry in place rather than creating a duplicate. Never store credentials or raw private material unless explicitly requested.

### Update and verify

After writing memory:

1. Update `memory/index.md` when needed.
2. Run `python3 <skills>/personal-memory/indexes.py` when a workflow or decision changed.
3. Run `python3 <skills>/personal-memory/gate.py --memory memory audit`. `<skills>` is the folder that holds the skill folders (`.claude/skills` in a workspace, `~/.claude/skills` for a global install); `python3` means `python` where that is the working command.
4. Trim any touched memory file warned about by the audit.
5. If the project is a git repo, commit the memory files written during this task, staging only those files.

If Python is unavailable, do the index work by hand, re-read the files, and say the audit was not run.

### Tell the user

In one short line, report the items recorded, their type, and their paths. If nothing qualifies, say: “Memory check: nothing worth capturing.”

Never store passwords, secrets, tokens, API keys, bearer strings, OAuth credentials, or credential-like configuration. Omit them automatically and never ask.
