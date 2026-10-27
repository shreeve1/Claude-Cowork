---
name: workflow-builder
description: |
  Turns a workflow you have in mind into a reusable skill, step by step — it drafts the steps, picks and customizes a specialist agent for each, and writes the finished skill.

  Use when the user wants to design, scaffold, or build a new workflow skill, pick and customize agents for a multi-step process, or mentions "workflow builder", "build a workflow", "create a skill that uses agents".
---

# Workflow Builder

## Workflow

Walk the user through building a reusable workflow skill — a new SKILL.md that orchestrates specialist agents drawn from `.claude/skills/workflow-builder/agents-library/`, customized and materialized into the produced skill's own `agents/` folder. Run it talk-it-through style: ask one question at a time in plain chat text and recommend an answer. Apply the 80/20 rule — spend questions on the vital few decisions (step structure, agent fit, customization, collisions) and state defaults for the trivial many.

The walkthrough has four phases, run in order.

### Phase 1 — Goal, name, description, and seed

1. Read `CONTEXT.md` and `memory/decisions/index.md` (decisions sit in `memory/decisions/<topic>/`) so you build on agreed language and prior conventions. Create both lazily — only when you have something to write (a resolved term or a settled decision).
2. Ask the user to state the workflow goal in plain language: what business process should this skill run, and what are they automating or scaffolding?
3. Propose a short name for the skill, derived from the goal, in all lowercase with hyphens between words (e.g. `launch-newsletter`, `onboard-client`). Recommend one; user confirms or overrides.
4. Draft the produced skill's `description` frontmatter to the writing-great-skills bar (see "Authoring bar for the produced skill" below; if you have a skill-writing guide, apply it): front-load the skill's leading word, give one trigger per branch (collapse synonyms that rename a single branch), and cut identity the body already carries. Recommend it; user confirms or edits. Completion criterion: the description front-loads a leading word and carries one distinct trigger per branch, with no duplicated triggers.
5. **Optional: seed from a published skill (don't reinvent).** Before authoring from scratch, check whether a comparable published skill can serve as a starting point — if you have a published-skill directory and a scaffolder available, load and follow them. Run the scaffolder's discovery, audit gate, and fetch/review against this goal; only skills that clear its security-audit gate are eligible. If a good base clears the gate and the user confirms it, use its customized SKILL.md as the **skeleton** for the produced skill and carry it into Phase 2. When run as a seed, the scaffolder hands back the customized skeleton without writing a file — this skill performs the single write in Phase 4. If nothing clears the gate or fits, say so in one line and author from scratch. This is a seed, not a requirement — the produced skill is still written to this skill's authoring bar and wired to local agents (Phases 2–4) regardless of whether a base was found.

### Phase 2 — Step list (what, not who)

1. From the stated goal (or the seeded skeleton, if one was found), propose an ordered list of steps. Each step is a unit of work with a single deliverable. Name what happens and what each step produces; agents come in Phase 3.
2. Grill the step list like talk-it-through grills a plan: one question at a time, recommend an answer, prune low-stakes branches. Common challenges:
   - Missing steps (was review, handoff, QA, or sign-off skipped?)
   - Fused steps (should "research and draft" be two steps with different agents?)
   - Order errors (does step 3 actually depend on step 5's output?)
3. Lock the final ordered step list and confirm it back to the user in plain text.

### Phase 3 — Pick, customize, and materialize an agent per step

For each step in the locked list, in order:

1. Read `.claude/skills/workflow-builder/agents-library/index.json` (the catalog in the skill folder) and filter by keyword match against the step's deliverable, matching on `name` and `description`. Narrow by `division` only when the user names one or the step is domain-specific enough that a division is obvious.
2. Surface 3–8 candidate agents as a plain-text list, each with `division / short name` and the catalog's one-line description. Keep the list to candidates, not the whole library (see the count in `.claude/skills/workflow-builder/agents-library/index.json`).
3. Recommend one agent for the step, with a one-line rationale tying the agent's specialty to the step's deliverable.
4. User confirms or overrides. When the user names an agent outside your candidates, verify it exists in `.claude/skills/workflow-builder/agents-library/index.json` before accepting — typos happen.
5. **Customize** the picked agent: read the source `.claude/skills/workflow-builder/agents-library/<division>/<short-name>.md`, then propose edits that scope its persona to this step's deliverable and this workflow. Confirm the customizations with the user.
6. **Materialize** it: create `.claude/skills/<name>/agents/` if missing, then write the customized copy to `.claude/skills/<name>/agents/<short-name>.md`. Use the library short name (the `slug` field in `index.json`) as the filename base; the materialized file is a self-contained persona doc (its own frontmatter `name`/`description`), not a subagent registration. When one base agent serves more than one step, give each a per-purpose short name (e.g. `researcher-intake`, `researcher-qa`) so the copies stay distinct. If the target file already exists, refuse and ask (overwrite / save-as-new-slug / cancel) — leave existing files intact until the user chooses.
7. Lock the agent for that step and note the deliverable. Move to the next step.

Return to Phase 2 at any time to add, remove, reorder, or rephrase steps; on return, re-confirm the step list before resuming Phase 3. Agents already locked for unchanged steps stay locked.

Default to one agent per step; descend into "two agents for one step" only when the user raises it and the step genuinely needs it. When no agent in the library is a reasonable base for a step, say so — the user can split the step, redefine the deliverable, or run the step with the generic assistant (no materialized agent).

### Phase 4 — Write the produced skill

1. Create `.claude/skills/` if missing. Check whether `.claude/skills/<name>/SKILL.md` already exists; if it does, refuse and ask (overwrite / save-as-new-name / cancel), leaving the existing file intact until the user chooses.
2. Compose the produced SKILL.md to the authoring bar below:
   - Frontmatter: `name` and `description` from Phase 1.
   - A `## Workflow` section of ordered steps. Each step states what to do, what it produces, and **ends on a checkable completion criterion** — exhaustive where it matters, so the agent can tell done from not-done and does not stop early.
     - For a step with a materialized agent, name it by path: "Read `.claude/skills/<name>/agents/<short-name>.md` and take on that persona for this step." The session adopts the persona inline; it never spawns a registered subagent and never copies agents back into the library.
     - For an agent-less step, write a plain instruction with no persona line.
   - Inline what every run needs; disclose branch-specific detail to a pointer file only when the produced skill branches.
   - Prompt the target behaviour positively; keep a prohibition only as a guardrail you cannot phrase positively, paired with what to do instead. Note the inputs, outputs, and permissions the skill needs, and confirm before any destructive action.
3. Write the file to `.claude/skills/<name>/SKILL.md` with a file-write tool (never paste the whole skill into chat) so the skill is on disk and activateable immediately.
4. Validate to the bar before reporting done: frontmatter `name`/`description` present; the description front-loads its leading word and carries one trigger per branch; every step ends on a checkable completion criterion; every `agents/<short-name>.md` the skill references exists on disk; no obvious no-ops or duplication. If the skill was seeded from a published skill, carry through the provenance line the scaffolder added. Fix any miss before finishing.
5. Tell the user the exact workspace-relative path(s): the produced skill and every materialized agent.

## Supporting Information

### Skill loading

- Skills are loaded from `.claude/skills/<name>/SKILL.md` directly; edits to the repo path are live immediately.
- Materialized agents in `.claude/skills/<name>/agents/<short-name>.md` are adopted inline by the produced skill — the produced skill instructs the session persona, it never spawns a registered subagent and never copies agents back into the library.

### Authoring bar for the produced skill

Apply these writing-great-skills principles to the produced SKILL.md so it stays predictable. The leading words — *description*, *branch*, *information hierarchy*, *completion criterion*, *no-op*, *duplication*, *sediment*, *negation*, and the rest — are defined in a skill-writing guide if you have one; read it when you need a term's full meaning:

- **Predictability first.** A skill exists to make the agent take the same *process* every run. Every rule below serves that.
- **Description does two jobs:** state what the skill is, and list the branches that trigger it. Front-load the leading word. One trigger per branch — collapse synonyms that rename a single branch. Keep it to triggers plus a reach clause; cut identity already in the body.
- **Information hierarchy.** Steps are the primary tier: ordered actions, each ending on a *checkable* completion criterion. Push reference (definitions, rules, facts) below the steps or, when the top bloats, out to a linked file reached by a context pointer.
- **Completion criteria.** Make each step's "what to produce" checkable and, where it matters, exhaustive ("every item accounted for", not "produce a list") so the agent does not stop early.
- **Prune.** One source of truth per meaning. Delete no-op lines the model already obeys by default. Cut duplication and stale sediment.
- **Leading words.** Anchor recurring behaviour in a compact pretrained concept (a single strong word) rather than restating a triad across three sites.
- **Prompt the positive.** State the target behaviour rather than steering by prohibition; keep a "don't" only as a hard guardrail you can't phrase positively, paired with what to do instead.

workflow-builder owns the orchestration design (steps + agents); the authoring bar owns how the produced SKILL.md is written well.

### Relationship to a published-skill seed

Phase 1 (step 5) optionally seeds the produced skill from a published-skill directory before authoring from scratch, when a scaffolder is available. The scaffolder owns directory discovery, the security-audit gate, and customizing a fetched skill; workflow-builder owns wiring local agents into the seeded skill's steps. workflow-builder runs the scaffolder inline as a sub-procedure; a scaffolder is also usable standalone for "find and adapt one skill".

### Shared memory with talk-it-through

This skill shares `CONTEXT.md` and `memory/decisions/` with `talk-it-through` so the two reinforce each other. Formats are defined once in talk-it-through's folder and referenced from here:

- `CONTEXT.md` format: `.claude/skills/talk-it-through/CONTEXT-FORMAT.md`
- Decision format: `.claude/skills/talk-it-through/DECISIONS-FORMAT.md`

These are referenced by relative path. If `talk-it-through` is renamed or moved, update the paths above to match. Read both at the start of a session when unsure how to structure a term or decision entry.

### Maintaining CONTEXT.md inline

When a term is resolved during the walkthrough (e.g. the user gives a precise name for a role, document, or status specific to this workflow), update `CONTEXT.md` right there using the format above. Do not batch. Keep `CONTEXT.md` a glossary only — no procedure, no task lists, no rationale.

### Wrapping up — record conventions (not skill content)

At wrap-up, auto-record to `memory/decisions/` following the same flow as talk-it-through — just record, without asking "do you want to record this?".

Record **workflow-building conventions only** — choices that change how future workflow-builder runs behave:
- Output shape decisions (e.g. "inline steps, no manifest"; "agents materialized to the produced skill's `agents/` folder, adopted inline").
- Invocation pattern reaffirmations or deviations.
- Walkthrough order changes.
- Collision handling preferences.

The content of the produced skill (which agents, which steps) lives in the produced SKILL.md and its materialized agents, not in memory. Write a new decision file only when a convention actually changes or a genuinely new one is settled.

After writing decisions: run `python3 .claude/skills/personal-memory/indexes.py` (decisions are listed in the generated `memory/decisions/index.md`, not in `memory/index.md`), run `python3 .claude/skills/personal-memory/gate.py --memory memory audit`, then commit per "Commit at the end of every task" in `CLAUDE.md`.

### Agents library reference

- Catalog (read this): `.claude/skills/workflow-builder/agents-library/index.json` Each entry has `division`, `slug` (the agent's short name), `name`, `description`, `color`, `file`.
- README: `.claude/skills/workflow-builder/agents-library/README.md` — layout, invocation patterns, editing rules.
- Agent files: `.claude/skills/workflow-builder/agents-library/<division>/<short-name>.md` — YAML frontmatter + Markdown body. Read the chosen file to customize it before writing to `.claude/skills/<name>/agents/<short-name>.md`.

Picking mechanics live in Phase 3; this section is the catalog map only.

### Hard rules

- One question at a time in plain chat text.
- Recommend an answer for every real question.
- Seed before authoring (optional): if you have a scaffolder, run its discovery + audit gate; adopt an external base only when it clears the gate and the user confirms; otherwise author from scratch.
- Materialize each picked agent as a customized copy at `.claude/skills/<name>/agents/<short-name>.md`; the produced skill adopts it inline by that path. The produced skill invokes no registered subagent and writes no agent back into `.claude/skills/workflow-builder/agents-library/`.
- Create `.claude/skills/<name>/agents/` if missing.
- On an existing skill or agent file, refuse and ask — leave it intact until the user chooses.
- Write real files (never paste whole skills/agents into chat) so the skill is on disk immediately.
- Author the produced skill to the writing-great-skills bar above (front-loaded description, per-step completion criteria, progressive disclosure via a skill-writing guide if you have one, leading words, pruning, prompt positive).
- Apply 80/20: stop grilling when remaining branches are low-stakes; state defaults and move on.
