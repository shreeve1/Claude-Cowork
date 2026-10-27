# Weekly memory sweep

Automatic capture only adds. The sweep is the other half: once a week it deletes old work files, re-checks stale notes, merges duplicates and trims oversize files, so `memory/` and the work folders stay small. It is optional. Without it the owner runs it by typing: `Run the personal-memory skill, section Weekly Sweep.`

Set it up once, after first setup is finished and the owner has used the workspace for a few days. Ask the owner each point below; do not pick for them.

## 1. Check it is safe here

- Git must be present, the workspace folder must be the top of its own repository, and its files committed. The sweep deletes a file only when its bytes equal the copy git last committed, so every deletion can be undone with `git checkout <commit> -- <path>`. In a folder that is not a repository top, or without Git, it deletes nothing; tell the owner and stop.
- Python 3.11 or newer must be present (`sweep.py`, `gate.py`).
- Run `python3 .claude/skills/personal-memory/sweep.py` (no flag). It lists what it would delete and deletes nothing. Show the owner the list.

## 2. Decide with the owner

- **When.** Default: Monday 09:00, the owner's own time zone.
- **Retention.** Default: `.sessions/` and `artifacts/` files older than 90 days. A file a note or skill names is kept, and `artifacts/startday/` is never swept. The numbers are `RULES` at the top of `sweep.py`. `reports/`, `memory/` and `clients/` are never aged out.
- **Who deletes.** The default is that the run deletes by itself. Tell the owner the safety net: only files identical to the committed copy, and one commit per sweep to read back.

## 3. Pick a runner

The sweep needs an agent for the judgement steps (stale notes, merges), so the schedule starts the agent headless with this prompt: `Run the personal-memory skill, section Weekly Sweep. Unattended: finish without asking questions.`

| Computer | Scheduler |
|---|---|
| Linux | a systemd user timer (below) |
| macOS | a `launchd` agent, `StartCalendarInterval` Weekday 1, Hour 9, Minute 0, one `ProgramArguments` entry per word of the command |
| Windows | Task Scheduler: weekly, Monday, 09:00; action runs the command with the workspace as "Start in" |

| Agent app | Headless command |
|---|---|
| omp | `omp -p --no-session --no-extensions --tools read,grep,glob,edit,write,bash --cwd <workspace> "<prompt>"` |
| Claude Code | `claude -p "<prompt>"` with the workspace as the working folder |
| Codex | `codex exec "<prompt>"` with the workspace as the working folder |

Use the owner's agent. If it has no headless command, use its own scheduled-task feature (`startday-spec`, `references/runners.md`, "Pick one") with the same prompt. Remote or cloud runners cannot see this folder: do not use them.

An unattended run must not stop to ask, and nobody watches it, so give it the fewest tools that do the job. `--tools` limits only the agent's built-in tools: connectors the app is configured with (ticket, mail, files in other systems) may stay reachable, and the prompt's ban on them is an instruction, not a lock. Tell the owner this. If the owner cannot accept it, disable those connectors for this run in the app's own settings, or run it from a profile that has none. End the prompt with: `Touch only memory/, .sessions/, artifacts/ and the clients/ hub files the skill names; call no client, ticket or mail tool.` Do not add `--auto-approve` or a similar flag until the test run in step 5 behaved, and tell the owner that flag lets the run execute commands without asking.

### Linux timer

`~/.config/systemd/user/memory-sweep.service`:

```
[Unit]
Description=Weekly memory sweep

[Service]
Type=oneshot
WorkingDirectory=<workspace>
ExecStart=<agent headless command from above>
TimeoutStartSec=45min
```

`~/.config/systemd/user/memory-sweep.timer`:

```
[Unit]
Description=Weekly memory sweep

[Timer]
OnCalendar=Mon *-*-* 09:00:00 <owner's time zone, for example America/Los_Angeles>
Persistent=true

[Install]
WantedBy=timers.target
```

Then `systemctl --user daemon-reload`, `systemctl --user enable --now memory-sweep.timer`, and `loginctl enable-linger $USER` so it runs while logged out. `Persistent=true` runs a missed Monday when the computer wakes.

## 4. Check the schedule

- Linux: `systemd-analyze --user verify memory-sweep.service memory-sweep.timer`, then `systemctl --user list-timers memory-sweep.timer`: the next run must show the right day and time.
- Other systems: read the next-run time in the scheduler.

## 5. Test run, then trust it

1. Start the service once by hand (Linux: `systemctl --user start memory-sweep.service`; others: "Run now"). Wait for it to finish.
2. Confirm `git log -1` shows `memory: weekly sweep <date>` (or no commit if nothing needed changing), and the run asked no questions.
3. Show the owner what it deleted or changed. Undo anything wrong with `git revert <commit>`.
4. Write down how to stop it: Linux `systemctl --user disable --now memory-sweep.timer`; others, pause or delete the scheduled task.

Do not call it working until the owner has seen step 5.
