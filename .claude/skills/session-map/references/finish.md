# Finish, pause or drop

Use when every stage is Done or Dropped, or the owner pauses or ends the effort.

1. Audit with no Todo, Active or Waiting stages.
2. Verify the Destination's own check fresh and end to end. If it fails, add a stage; the map is not finished.
3. When stages had only individual reviews, run a proportionate whole-effort review, such as a reviewer subagent on the combined diff.
4. Clean up created branches, worktrees, scratch plans and temporary services. List what was removed.
5. Add `## Outcome` after Destination: truth against the Destination, dropped work and reasons, follow-ups as new maps or tickets, and one to three lessons.
6. Carry durable decisions and facts into project memory, docs or ADRs. Future sessions look there, not in finished maps.
7. Set status done, or dropped with the reason in Outcome; set Next to `None`; commit only after `python3 <skill folder>/scripts/map.py audit <map path> && git commit -m "map: finish <slug>" -- <your files>`. Push when the branch has an upstream.
8. Report evidence to the owner.

To pause, set status paused and add a Log line explaining why and what restarts the work.

Done when the Destination is freshly proven, Outcome is written, knowledge is carried out, and the final status is committed.
