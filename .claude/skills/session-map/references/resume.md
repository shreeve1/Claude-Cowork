# Resume a map

Use when a session starts on a map, the owner names an effort that has one, or asks where it stands.

1. Work from the repository root. Pull with `git pull --rebase` only when `git rev-parse --abbrev-ref @{u}` succeeds.
2. Run `map.py status`; use `status --all` when the owner asks about a finished effort. Match a loose name to slug or title. If status finds nothing, check the repository root and the place it says it searched before asking the owner which repo.
3. Take the map path from status output, audit it, then read the whole map. Read only files linked from frontier briefs.
4. Reconcile drift: inspect `git log <sha>..HEAD`, `git status`, branches and worktrees for Active work. Record unrecorded work through [update.md](update.md) before starting new work.
5. Choose the owner's named stage, else the first ready stage, else an Active stage whose session stopped; check its claim time and the Log. If nothing is ready, state what is waiting and ask only the blocking question.
6. Claim the chosen stage before reading inputs or doing stage work: run `python3 <skill folder>/scripts/map.py claim <map path> <id>`. Claim a Waiting stage after its gate resolves the same way. An Active stage is already claimed; resume from **Where it stopped**, never from its beginning. Check commits named from other repositories by hand.
7. Tell the owner in two to four lines where things stand and what this session will do.

A “where are we?” question uses status and the map only; do not begin stage work.

Done when you can name the chosen stage, its done-when check and inputs, and account for every commit since the map last changed.
