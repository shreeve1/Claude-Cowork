---
name: brainstorm-idea
description: |
  Brainstorm, riff on, or creatively explore a raw idea with optional project context and web research before planning or implementation.

  Triggers when user wants to explore possibilities rather than commit, including phrases like:
  - "brainstorm" / "let's brainstorm"
  - "I have an idea" / "I'm toying with"
  - "riff on this" / "thinking out loud"
  - "what could this become" / "where could this go"
  - "what if we..." / "could we..."
  - "explore possibilities" / "kick around some ideas"
---


# Brainstorm Idea

Use this skill for exploratory, idea-generating conversations where the goal is discovery, not commitment.

Prefer this skill when the user wants to expand possibilities, make unexpected connections, compare directions, or see where a concept could go.

Do not use it when the user already wants a concrete implementation plan, code changes, ticket research, formal requirements, or strict technical design.

## Output Style

- Keep chat responses concise and idea-forward.
- Lead with useful ideas, not process narration.
- Use short bursts, bullets, and options.
- Ask one focused question at a time when needed.
- Do not create long reports unless user asks to save or formalize output.

## Tools You'll Use

- Respond in normal chat, or use `AskUserQuestion` when multiple-choice input helps.
- Use `Read`, `Glob`, `Grep`, and limited `Bash` for repo inspection.
- Use `Agent` subagents for parallel research or codebase exploration.
- Use `web_fetch` for known URLs, and background-only search through this workspace's browser extensions when available.

## Workflow

### 1. Capture Core Idea

Identify:

- core idea in one sentence
- why user cares, if stated
- any requested exploration mode
- any project path or workspace context
- any boundaries: practical, wild, technical, business, client-safe, cost-sensitive, time-sensitive

If the idea is missing or too vague, ask one concise clarification question and stop.

If the user supplied a project path, verify it exists before relying on it. Use `Glob` (or `ls` via Bash) for directories. Use `Bash` only for commands that are needed and safe.

If no project path exists, continue without project context.

### 2. Gather Lightweight Context

If current workspace or supplied project context matters, gather only enough context to brainstorm well.

Look for:

- what project or workflow does
- relevant stack, architecture, documents, or process constraints
- existing skills, agents, docs, tickets, or artifacts connected to idea
- natural integration points
- gaps or friction points idea might address

Preferred inspection order:

1. Read `CLAUDE.md`, `README*`, `wiki/index.md`, or obvious docs when relevant.
2. Use `Glob` and `Grep` for targeted discovery.
3. Optional: use a helper script for broad repo context only when one actually exists in the workspace; otherwise skip this step.
4. Use `Agent` subagents for medium/broad codebase exploration, not for tiny lookups.

Keep context summary short. This is not design review.

### 3. Frame Idea Back

Before generating many ideas, restate framing in 1-2 sentences.

Then ask one focused question only if answer will materially improve brainstorming.

Useful question patterns:

- "What mode helps most: wild ideas, practical directions, technical angles, or surprising analogies?"
- "What sparked this?"
- "What constraint matters most: speed, cost, user delight, reliability, security, or reuse?"
- "Should this stay exploratory, or should promising ideas turn into next steps?"

When a few clear modes fit, use `AskUserQuestion` with options such as:

1. Broad creative exploration
2. Practical product directions
3. Technical concept exploration
4. Surprising cross-domain ideas
5. Mix of all

### 4. Pick Exploration Angles

Turn current understanding into 3-5 distinct angles. Avoid minor wording variants.

Good angle mix:

- product or user experience
- technical system design
- workflow or operations
- business model or adoption path
- adjacent-domain analogy
- contrarian or failure-mode perspective

Present angles briefly and ask how to proceed when needed:

- explore all angles
- focus top 2-3
- revise angles
- skip research and riff directly

If the user clearly wants immediate riffing, skip the permission loop and continue.

### 5. Background Research Only When It Adds Energy

Use research when external evidence, examples, competitors, implementation patterns, or market context will improve ideas.

Skip research when topic is personal, speculative, private, internal-only, or already clear enough.

Research safety:

- Do not send client-identifying details, private tickets, user emails, internal hostnames, private logs, or secrets to public search/pages.
- Search generic terms, product names, errors, and public concepts.
- Use `web_fetch` for known URLs.
- Use background-only search through this workspace's browser extensions when available.
- Do not open visible browser UI during this skill's research phase.
- If search is needed and no background search extension exists, ask user for URLs or continue without web research.
- If needed search capability is unavailable, check for a background-search extension before saying unavailable.

For parallel research, use `Agent` subagents. Assign one angle per subagent:

```text
Research this brainstorming angle for idea: <idea>

Angle: <angle>
Context: <short safe context>

Return:
- 3-5 concise insights
- 1-2 surprising or contrarian findings
- useful source URLs, if any
- no private/client-identifying data
Keep output compact and idea-generative.
```

Synthesize findings into short briefing before riffing.

### 6. Riff Collaboratively

Core behavior:

1. Seed discussion with 2-4 interesting directions.
2. Build on user reactions instead of forcing fixed structure.
3. Connect across domains, patterns, audiences, and technologies.
4. Offer alternatives, combinations, "what if" variants, and smaller versions.
5. Name tensions and tradeoffs without killing momentum.
6. Periodically summarize emerging themes.

Useful idea moves:

- "Smallest useful version"
- "Weird version"
- "Enterprise version"
- "Ops-friendly version"
- "AI-native version"
- "Manual-first version"
- "What this replaces"
- "What this should never become"
- "Failure mode worth designing around"
- "Adjacent domain analogy"
- "Reality check: what would make this fail?"

When a direction gains momentum, offer an optional reality check before moving on: what has to be true for this to work, what would kill it, and the cheapest way to test the riskiest assumption. Keep it brief — this validates without killing momentum.

If one direction becomes implementation-oriented, say so and note that the user can move into a dedicated planning or implementation effort. Do not start implementation unless user explicitly approves.

### 7. Capture Session When Useful

When session winds down, summarize:

- core concept
- most interesting directions
- important connections or tensions
- promising next moves
- open questions

Ask whether the user wants the summary saved unless they already requested an artifact.

Default artifact path:

- `brainstorming/idea-<topic-slug>-<YYYY-MM-DD>.md`

Use normal prose in saved Markdown. Do not include secrets or raw private material. Mention exact workspace-relative path after writing.

Use these sections in the saved file: title (`# Idea Exploration: <idea>`), Context, What Sparked This, Research Findings, Ideas Explored (per-direction: why interesting / risks or tensions / possible extension), Connections Made, Promising Next Steps, and Open Questions.

## Final Report

When wrapping up, report briefly:

- idea explored
- whether project context was reviewed
- whether web research was performed
- strongest directions that emerged
- any file written and workspace-relative path
- natural next step

## Example

**User:** "I'm toying with the idea of a status page that writes its own incident updates."

**Skill (frame + mode):** "So: an AI-drafted status page that turns raw signals into human-readable incident updates. Want wild ideas, practical directions, or technical angles?"

**User:** "Practical, with one technical angle."

**Skill (riff with angles + reality check):**
- *Smallest useful version:* draft updates from existing alerts, human clicks publish.
- *Ops-friendly version:* tone presets (calm/transparent/terse) so updates match the incident's severity.
- *Technical angle:* subscribe to the alerting webhook, summarize with an LLM, queue for one-tap approval.
- *Reality check:* the riskiest assumption is trust — a wrong auto-update erodes credibility fast. Cheapest test: run it in shadow mode, draft-only, and compare against what humans actually post.

The loop stays short, builds on the user's steer, and pressure-tests before momentum runs away.
