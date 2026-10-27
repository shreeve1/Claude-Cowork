<!-- markdownlint-disable-file MD041 -->
<!-- Paste the sections below into the project's CLAUDE.md or CLAUDE.md, in place of any wiki section. Replace the skills-folder placeholder in the sections below with the path chosen in memory-setup step 2. -->

## DO THIS FIRST: read memory before your first reply

On your FIRST response in a session, before you answer, plan, load any skill or ask any question:

1. Read `memory/index.md`, `memory/glossary.md` and `memory/rules.md`, then every file the `Always` row of `memory/rules.md` names. If a file does not exist, note it and move on. Do this even when the request seems unrelated or is itself a simple read.
2. Before each task, load every row of `memory/rules.md` whose When fits it: its Lead skill runs the task, its Also load files add content.
3. Treat index rows as pointers, not facts. Open the linked file before relying on a row.

## Memory capture: check at the end of every task

Not optional, and the user does not have to say "remember". Before reporting a task complete, check the session for these triggers:

- The user **corrects you** or overrides something you did.
- The user **states a rule or preference** about how to work here.
- The user **describes how a process goes**, or sets a boundary on one.
- A **decision is settled** that a future session would otherwise re-litigate.
- **You discover a non-obvious fact likely to come up again** (a fix, a gotcha, a tool quirk, how this project's stack is set up) that a future session could not cheaply rediscover.

Write everything that qualifies once, at the end of the task, with the `personal-memory` skill. Do NOT ask first. End the reply with one line per item: `Memory saved: <path> - <short summary>`. If nothing qualified: `Memory check: nothing worth capturing.`

Does not qualify: one-off task details, the status of work still in motion (save it once, when it settles), temporary instructions, anything memory or the project's own docs already state correctly. Never store credentials; omit them automatically.

## Project memory

`memory/` holds this project's durable memory, operated by the `personal-memory` skill at `<skills>/personal-memory/`. `memory/README.md` is the layout contract; read it before creating a memory file.

- **Write:** once per task, to the right file (workflows and decisions in a topic folder from `memory/schema.json`), update `memory/index.md`, then from the project root run `python3 <skills>/personal-memory/indexes.py` if a workflow or decision changed, `python3 <skills>/personal-memory/hubs.py` if a Client Memory note changed, and `python3 <skills>/personal-memory/gate.py --memory memory audit` until it exits 0. Without Python, use the skill's manual checks instead.
- **Conflicts:** a new item that contradicts memory overwrites it in place. Files state only what is true now.
- **Git:** if this project is a git repo, commit the memory files you wrote with the task (stage only your own). If not, the capture ends after the audit.
- **Rules:** `memory/rules.md` routes tasks to skills and files, one row per trigger, pointers only. Add a row through the `personal-memory` skill.
