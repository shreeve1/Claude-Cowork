# Rules

Read at session start. Load every Always row now. Before each task, load every row whose When fits.

- One lead per task. The Lead skill runs the workflow, including how research is done. Also load adds content, style and checks, never workflow steps. A row's Note can scope how a check is reported.
- When two rows offer a lead, the more specific When wins; on a tie, the one matching what the owner literally asked.
- A lead's limits stay inside its own workflow.
- Rows point; they hold no guidance. Content lives in the files they name.
- New rule: add a row (personal-memory "Rules"). `gate.py audit` fails a row naming a missing skill or file, and a preference or email file no row reaches.

| When | Lead | Also load | Note |
|---|---|---|---|
| Always | | `memory/preferences/document-scaffolding.md`, `memory/preferences/cowork-environment.md` | |
| Work on one client | | `memory/clients/_hubs/<short>.md` | Short name from the glossary. Setup (the Tracking model step in the setup docs) renames this row to the owner's word and folder, or deletes it. |
| Shorthand name of a client, person or system | | `memory/glossary.md` | |
| A word that sounds like a defined term | | `CONTEXT.md` | |
| Using a tool, connector or workstation setup | | `memory/workflows/index.md` | Open the entries that fit. |
| A choice that may already be decided | | `memory/decisions/index.md` | |
| A hard-to-reverse choice only the owner can make | skill `talk-it-through` | | Routine choices get a stated default instead. |
| Problem outside the owner's usual work, or the owner asks for an expert view | skill `professional-guidance` | | |
| Saving, pruning or checking memory | skill `personal-memory` | | |
