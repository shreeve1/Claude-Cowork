---
name: session-map
description: Use when work outgrows one session, the owner asks to map an effort, or a session must resume, update, audit, review or finish a map in docs/maps/.
---

# Session maps

A map in `docs/maps/` is the shared state for an effort that spans sessions. Each new session starts cold; the map and linked files are the only state it can rely on.

## Rules

In the commands below, `python3` means `python` where that is the working command (often on Windows).

- From the map's repository root, run `python3 <skill folder>/scripts/map.py status` (the skill folder holds this SKILL.md; in Claude Cowork, find its installed folder for this session rather than assuming a fixed path). Take the map path from status output; never guess. Run `python3 <skill folder>/scripts/map.py audit <map path>` at start and end.
- Claim a stage before stage work: `python3 <skill folder>/scripts/map.py claim <map path> <id>` marks it Active and commits only the map.
- Brief only the frontier: Active stages and Todo stages whose dependencies are Done. Later work stays fog until its inputs are known.
- The owner decides the destination, scope and whether requested work is added or dropped. Agents choose the how and attribute their decisions.
- End every session that worked on a map with `update.md` and a commit, including mid-stage. The sole exception is a read-only status answer.
- For a small stage, its brief serves as the design (no separate design doc) and includes **Approaches:**. The owner approves the destination and stages; how to build a small stage is the agent's call, so build it without another approval round. For a larger stage, brainstorm briefly (skill `brainstorm-idea` where installed), then write and link a spec and plan before execution.
- A repo with maps has one line in `CLAUDE.md`: multi-session efforts live in `docs/maps/`; use session-map to continue one. The first map adds it in the same commit; the checker warns when missing.
- Outside Git, keep the map at the same path; skip commit, push and drift steps and say so in the session report.
- Parallel sessions in one folder follow the coordination rules in [update.md](references/update.md).
- If a subagent or another session executes a stage, its brief names the map and stage. The session that started it verifies its result and updates the map.

## Moments

| Moment | Trigger | Read |
| --- | --- | --- |
| Start | Work outgrows a session or the owner asks for a map | [start.md](references/start.md) |
| Resume | A session starts on a map or the owner asks where it stands | [resume.md](references/resume.md) |
| Update | A map session ends or discovers a durable result | [update.md](references/update.md) |
| Audit | Start/end checks, drift, a gap, route review or the owner asks | [audit.md](references/audit.md) |
| Review | A stage ends or the route changes | [review.md](references/review.md) |
| Finish | All stages end, or the owner pauses/ends the effort | [finish.md](references/finish.md) |

Use [template.md](references/template.md) for field rules and [example.md](references/example.md) for a filled map's shape. Follow only the reference for the moment at hand.
