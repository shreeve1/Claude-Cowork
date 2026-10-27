# Tracking model (before filing old notes)

Every owner has people or things they keep coming back to and need remembered in a steady shape: clients, students, patients, properties, customers, projects, a team. This workspace stores them as Client Memory: one short name per thing in `memory/glossary.md`, one small note per lasting fact (subject, verified date, source), a generated hub per thing, and a row in `memory/rules.md` that loads the hub when the agent works on it. The shipped words say "client". The owner's own word goes into the folder name (`client_folder` in `memory/schema.json`) and into `CONTEXT.md`, so it reads naturally to them.

In a project that is not a full starter workspace, read "Applying this outside a full workspace" below first; it adjusts steps 4 to 6.

Ask: **"What people or things do you keep coming back to, and what do you need remembered about each?"** Skip if the owner already answered.

If the owner has such things:

1. Note the owner's word for them (for example "student") and turn it into a folder name: one lowercase word, usually plural (`students`). Set `"client_folder": "students"` in `memory/schema.json`. The key is optional and defaults to `clients`; the memory scripts, the commit hooks and the audit all follow it. Set it before any note exists. If `memory/clients/` or `clients/` already holds files, first move both folders to the new name with `git mv`, run `python3 <skills>/personal-memory/hubs.py`, and fix the hub rows in `memory/index.md`. Exception: if `.claude/skills/startday/` exists, leave `client_folder` unset; startday and the shipped Procedures use `clients/`.
2. Add each thing to `memory/glossary.md` as a short name plus identity, in a table under a `## Clients` heading. Keep the heading `Clients` whatever the owner's word; scripts read it.
3. Propose 3 to 6 subjects, the kinds of lasting facts the owner named (for example `contacts`, `preferences`, `history`). Lowercase single words. With the owner's OK, add them to `client_subjects` in `memory/schema.json`. Keep every subject already listed there and every subject an existing note uses; only add. Remove one only after its notes are moved to another subject or the owner agrees to drop them, otherwise the audit fails. Leave `client_dirs` as shipped unless the owner wants fewer document folders.
4. Add a `CONTEXT.md` entry saying the owner's word means Client in this workspace (`talk-it-through` keeps it).
5. `memory/rules.md` ships with a row that loads `memory/clients/_hubs/<short>.md` (`Work on one client` in a starter workspace, `Work on one tracked thing` from the project scaffold). Change its When to the owner's word and its path to the folder from step 1 (`memory/<client_folder>/_hubs/<short>.md`).
6. **Workspace only:** in `memory/preferences/document-scaffolding.md`, change `clients/<short>/` in the folder map to `<client_folder>/<short>/`.
7. Prove it: with `personal-memory`, write one real note for one thing and run `hubs.py`. Add the new hub's row under `## Client Hubs` in `memory/index.md` (the audit fails a hub without one), then run `python3 <skills>/personal-memory/gate.py --memory memory audit` and show the owner the hub. Without Python, write the hub row by hand and skip the audit.

If the owner has no such things: leave `client_subjects` empty, delete that row from `memory/rules.md`, tell the owner why, and skip steps 1 to 7. If they track some other kind of thing (projects, topics, a household), treat that as the thing and follow the steps above. Revisit this section whenever the owner's work changes.

## Applying this outside a full workspace

The section above is the workspace's tracking model. In a separate project, use the `<skills>` path chosen in setup step 2. Ask one question at a time with a recommended answer; if `talk-it-through` is absent, do that in this session. A hub is a small page linking the notes about one person or thing; call it that when speaking to the owner.

Settle the model before sorting, but wait for step 6 approval before writing facts or the proof note. An existing `memory/` keeps its content: propose any rename or schema change separately and get the owner's OK before applying it. If this scaffold has no client-loading row, add the row described above when tracking is used; otherwise there is nothing to delete. Change a folder map only if one exists.

Without git, use file tools to move existing folders after checking destination conflicts and preserving both sides. Without Python, write the hub and its index row by hand following `personal-memory`; verify its links and required fields manually. No tools need installing.
