# Runners

A runner starts the next startday turn during the day. The loop is optional: with no runner the owner types the turn prompt themselves (`startday` in a fresh session), and the result is the same.

Every runner below starts the same turn, the **poll turn**: one pass that reads all its state from files, so it works whether the runner keeps one session open or starts a fresh one each time.

## Pick one

| Runner | Where it is set up | Session each run | Needs | Fit |
|---|---|---|---|---|
| None | the owner types `startday` | fresh | nothing | Always works. The default until a runner is tested. |
| Claude Code Desktop local scheduled task | Code tab > Routines > New routine > **Local**; working folder = this workspace | fresh | app open, computer awake; one missed run catches up on wake | Good: local files, local MCP config, Python. Click **Run now** once and "always allow" each prompt, or later runs stall. |
| Codex app scheduled task (project-scoped) | Codex desktop > Scheduled; choose this workspace as the project, run in the local project, not a worktree | fresh (standalone task) | app running, computer on; sandbox must allow network for the ticket tools | Good once the sandbox allows the commands the turn runs. A worktree gets its own copy of the files, so ticks the owner made in the main folder are not seen. |
| Claude Code `/loop` | in an open session: `/loop 15m <turn prompt>` | same session | terminal session stays open; recurring tasks expire after 7 days | Good for a workday in one terminal. Restart it each morning. |
| omp `/loop --while` | in an open omp session: `/loop --while '<check script>' <turn prompt>` | same session | omp session stays open; a check script that exits 0 when there is work and 1 when the day is over | Event-driven: the turn runs the moment the check script sees a change. Needs a check script; the poll turn needs none. |
| Claude Cowork scheduled task | Scheduled > New task | fresh | see the warning | Only when the task runs **locally** with this workspace as its folder. |

Cowork warning: new Cowork scheduled tasks run remotely by default and see only connectors and files saved to the Claude account, not this folder, the local MCP config or Python. Anthropic's help article says a task that needs local files runs only locally, but how that is chosen differs by plan and app version. Set the task's folder to this workspace, then make one test run and confirm it wrote to a file in this workspace. If it cannot, use another runner. Source: https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-cowork

Remote runners (cloud routines, web tasks, Cowork remote runs) cannot reach the research files or tick boxes on this machine. Do not use them for startday.

## The turn prompt

One line, the same for every runner: `Run the startday skill: poll turn.` Set the cadence to the owner's check interval (every 15 minutes is a good default; Codex and Claude Desktop accept custom intervals when asked in a chat). The poll turn itself checks the clock, so runs outside working hours end in one line.

Limit the schedule to working hours (weekdays, from the owner's start time). The first run of the day starts the day, so a runner firing at midnight would start it at midnight. Where the app only offers "hourly", ask it in a chat for a custom schedule such as "every 15 minutes, weekdays 8am to 5pm".

One run at a time. A first run of the day can take longer than the interval. Claude Code Desktop skips a run while the previous one is still going; for other runners, check that they do the same, or pick an interval longer than a first run takes.

## Before trusting a runner

1. Run the turn once by hand in a fresh session; it must finish with no question to the owner.
2. Trigger the runner once ("Run now" or wait one interval). Confirm a file in this workspace changed (the activity log or a research file).
3. Tick one approval, wait one interval, confirm it was executed and read back.
4. Write down how to stop the runner at once: pause or delete the scheduled task, or `Esc` / cancel the `/loop`.
