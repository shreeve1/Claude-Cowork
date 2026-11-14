# Start a map

Use a map when brainstorming or planning finds stages needing separate design or verification, unknown results block later work, a design would exceed about two screens, or work spans days or machines. The owner can also say “map this”. From brainstorming, map the effort instead of writing one large design, then brainstorm only stage 1.

## Steps

1. Name the destination with the owner. Ask if the end state is unclear.
2. List stages breadth-first. Each stage should be one session that leaves working, committed results. Put unknowns in Open questions or coarse later stages; this is fog.
3. Split any stage needing more than about eight tasks or two separately verified systems.
4. Copy [template.md](template.md). Write briefs only for the frontier.
5. Show the owner the destination and stage list in one message. Stage order and briefs are the agent's how-calls.
6. On the first map in a repo, add one line to its `CLAUDE.md`: multi-session efforts live in `docs/maps/`; use session-map to continue one. Include this change in the map's start commit.
7. Commit only after `python3 <skill folder>/scripts/map.py audit <map path> && git commit -m "map: start <slug>" -- <your files>`. Push when the branch has an upstream.

When the repo already tracks this work elsewhere (saved tasks, issues or a plan), keep stage status only in the map and checklist detail in one place, linked from the brief's Starts from rather than copied. Do not require every session to update both.

When a stage needs the owner's answer, its brief says what can happen before the answer (research or a draft on a stated assumption) and what waits. Put questions at the end of a session's work, since asking ends the turn.

Charting is a session's work by default. Starting stage 1 in the same session is fine only when it is small.

Done when the map is committed, audit reports zero errors, the owner has approved the destination and stage list, and the first-map CLAUDE.md pointer is present when needed.
