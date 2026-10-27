# Where things go

Use this table when sorting old material. The owner approves what moves and what stays behind. Rows marked **workspace only** assume a full starter workspace; in another folder, use its existing document and skill conventions instead.

| What the owner has | Destination |
|---|---|
| A rule about how the agent behaves (tone, format, "always", "never") | A preference note in `memory/preferences/` plus a row in `memory/rules.md` (`personal-memory` skill) |
| A fact about the owner, their tools or machine | A doc note in `memory/docs/` |
| Lasting facts about a person or thing they track | A Client Memory note under the subjects settled in the tracking model (`personal-memory` skill, then `hubs.py`) |
| A process the agent runs, learned from use | `memory/workflows/<topic>/` (topics in `memory/schema.json`) |
| Verified steps the agent follows when a trigger comes up | A procedure in `memory/workflows/<topic>/` (`personal-memory` reference.md "Procedures"), saved only with the owner's yes |
| A runbook a person follows | The project's `docs/`, or wherever its runbooks already live |
| A settled decision | `memory/decisions/<topic>/` |
| Email or message style | `memory/email/` or `memory/voice/` |
| A shorthand name | A row in `memory/glossary.md` |
| A word used in a specific way | `CONTEXT.md` |
| Unsorted notes worth keeping | Sort now, or use `memory/raw/` (git-ignored) if the owner wants them kept as is, with credentials removed. |
| Raw material to keep as is (git-ignored) | `memory/raw/` |
| Their own skill (**workspace only**) | `.claude/skills/<name>/`, copied whole |
| An old copy of a shipped skill (**workspace only**) | Not copied; the shipped one wins. A difference the owner relies on becomes a preference note naming the skill. |
| Documents, reports, research (**workspace only**, uses the folder map) | The folder the folder map names (`memory/preferences/document-scaffolding.md`) |
| A whole instructions file | Split by the rows above. Lines that repeat shipped `CLAUDE.md` are dropped with the owner's OK. |
| A not-yet-built plan or decision | The project's own backlog or issue tracker, not memory; propose a new issue if no destination exists. |
| A fact the project's docs, code or existing memory already state | Linked, never copied. Point to the authoritative file when useful. |

Keep personal content out of shipped files: a later Release replaces them. In a full starter workspace this includes `CLAUDE.md`, shipped skills and setup docs; personal changes belong in memory. A short `CLAUDE.md` that only says "Read CLAUDE.md" is fine when the owner's app needs one.
