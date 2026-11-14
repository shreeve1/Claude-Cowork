# Update a map

Update at the end of every session that worked on a map, whether the stage finished or not. Record decisions and facts for later stages as soon as they arise.

1. Update the stage row and evidence. Mark Done only after [review.md](review.md). If unfinished, keep Active and write **Where it stopped** with completed work, remaining work and branch/worktree.
2. Record decisions with attribution. Replace a contradicted decision in place; Git keeps history.
3. Add facts later stages need under Found along the way.
4. For route changes, scope changes belong to the owner: record an Open question and stop short of acting. Splits, merges and reorders within scope are agent calls to record; retain IDs and Dropped rows with reasons.
5. Remove completed briefs and write briefs for newly ready stages using actual results, paths and names. Update Open questions; move answered questions to Decisions. When a human gate resolves, clear its Waiting note and Open question together.
6. Add one Log line. Commit only after `python3 <skill folder>/scripts/map.py audit <map path> && git commit -m "map: <slug> stage <id> <status>" -- <your files>`. Push when the branch has an upstream. On a pull or rebase conflict in separate clones, keep both Log lines, keep both decisions unless one replaces the other, and keep other sessions' rows; then rerun audit to recompute the frontier.
7. End with: `Continue docs/maps/<slug>.md with session-map: stage <id>.`

Start a new session only when the owner asks; use the `handoff` skill to write its continuation prompt.

## Parallel sessions in one folder

Commit only your files by name; stage files explicitly. Before editing a shared file, run `git status --short`. If another session has uncommitted edits in a file you need, do other work first, then wait for its commit and re-check `git log -1` about every minute. If it has not committed when you are otherwise done, make your edit and commit that file, naming the included edits in your message. Re-read shared map sections (Open questions, Decisions, Constraints, Found along the way) just before editing; change only your own lines and commit right after. When done-when requires another stage's row or brief, change it last, just before committing, and leave that stage's Status unchanged. Separate clones pull before editing and use the rebase-conflict rule above.

Done when audit is clean, the map is committed, and a fresh session can start the next stage from it alone.
