# Rules

Read at session start. Load every Always row now. Before each task, load every row whose When fits.

- One lead per task. The Lead skill runs the workflow, including how research is done. Also load adds content, style and checks, never workflow steps. A row's Note can scope how a check is reported.
- When two rows offer a lead, the more specific When wins; on a tie, the one matching what the owner literally asked.
- A lead's limits stay inside its own workflow.
- Rows point; they hold no guidance. Content lives in the files they name.
- New rule: add a row (personal-memory "Rules"). `gate.py audit` fails a row naming a missing skill or file, and a preference or email file no row reaches.

| When | Lead | Also load | Note |
|---|---|---|---|
| Always | | `memory/preferences/writing.md`, `memory/preferences/diagrams.md`, `memory/preferences/document-scaffolding.md`, `memory/preferences/cowork-environment.md` | |
| Drafting any email | | skill `antislop`, skill `antislop-copywriting` | Run the antislop Delivery Gate and copywriting checklist silently; mention only a FAIL and fix it before delivering. |
| A proposal, report or other document someone else will read | | skill `antislop`, skill `antislop-copywriting` | Run the gate silently; mention only a FAIL and fix it before delivering. |
| Designing a visual output: HTML page, PDF, slide, UI | | skill `antislop`, skill `antislop-ui` | Show the full antislop PASS/FAIL report with the deliverable. |
| Writing a research file | | `memory/preferences/research-documents.md` | |
| A question about a website, portal or web app, or a step blocked behind a web sign-in | | `memory/preferences/browser-shared-view.md` | |
| Work on one client | | `memory/clients/_hubs/<short>.md` | Short name from the glossary. Setup (the Tracking model step in the setup docs) renames this row to the owner's word and folder, or deletes it. |
| Shorthand name of a client, person or system | | `memory/glossary.md` | |
| A word that sounds like a defined term | | `CONTEXT.md` | |
| Using a tool, connector or workstation setup | | `memory/workflows/index.md` | Open the entries that fit. |
| The owner starts defining a procedure ("let's define a procedure for …") | | `memory/README.md`, `memory/TEMPLATES.md`, `memory/workflows/index.md` | Saves only with owner approval; README "Capture" has the flow, TEMPLATES "Procedure File" the shape. |
| Processing a meeting transcript, or the owner names who a meeting was with | skill `meeting` | `memory/preferences/meetings.md` | Settings first; ask the skill's First use questions when they are not set. |
| A task a saved procedure covers | | `memory/workflows/index.md` | Open and follow the matching procedure file. |
| A choice that may already be decided | | `memory/decisions/index.md` | |
| A plan, process, document, or ambiguous direction needs thinking through | skill `talk-it-through` | `memory/preferences/talk-it-through.md` | Recommendation first; ask only decision-changing questions. |
| Problem outside the owner's usual work, or the owner asks for an expert view | skill `professional-guidance` | | |
| Saving, pruning or checking memory | skill `personal-memory` | `memory/preferences/memory-maintenance.md` | Replace or merge in place before appending; sweep references after. |
