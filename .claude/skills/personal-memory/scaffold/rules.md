# Rules

Read at session start. Load every Always row now. Before each task, load every row whose When fits.

- One lead per task. The Lead skill runs the workflow. Also load adds content and checks, never workflow steps.
- When two rows offer a lead, the more specific When wins; on a tie, the one matching what the owner literally asked.
- Rows point; they hold no guidance. Content lives in the files they name.
- New rule: add a row (personal-memory "Rules"). `gate.py audit` fails a row naming a missing skill or file, and a preference file no row reaches.

| When | Lead | Also load | Note |
|---|---|---|---|
| Always | | | |
| Shorthand name of a host, service, person or system | | `memory/glossary.md` | |
| A word that sounds like a defined term | | `CONTEXT.md` | Delete this row if the project has no `CONTEXT.md`. |
| Work on one tracked thing | | `memory/clients/_hubs/<short>.md` | Template: rename to the project's word and folder when Client Memory is set up, otherwise delete. |
| The owner starts defining a procedure ("let's define a procedure for …") | skill `personal-memory` | `memory/TEMPLATES.md`, `memory/workflows/index.md` | Steps: personal-memory reference.md "Procedures". |
| A task a saved procedure or workflow covers | | `memory/workflows/index.md` | Open the matching file and follow it. |
| Saving, pruning or checking memory | skill `personal-memory` | | |
