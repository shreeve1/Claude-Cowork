# CONTEXT.md Format

`CONTEXT.md` is the team's shared glossary — the agreed meaning of the words you
use for people, documents, steps, and statuses in this work. It is not a
procedure, a checklist, or a record of decisions. It exists so that everyone
means the same thing when they say the same word.

Keep one `CONTEXT.md` at the workspace root.

Create sections only when they have real content. It is OK for a new `CONTEXT.md` to start with just a title, short description, and one resolved term.

## Structure

```md
# {Workspace or area name} — Shared Language

{One or two sentences on what this area covers and who it's for.}

## Language

**Client**:
The organization we hold a contract with and bill.
_Avoid_: customer, account, company

**Contact**:
A named person at a Client we communicate with day to day.
_Avoid_: client, user

**Ticket**:
A single tracked request or issue raised by a Contact.
_Avoid_: case, job, request

**Sign-off**:
The Client's written acceptance that work is complete.
_Avoid_: approval (use "approval" only for internal manager approval)

## Relationships

- A **Client** has one or more **Contacts**
- A **Contact** raises one or more **Tickets**
- A **Ticket** is closed only after **Sign-off**

## Example dialogue

> **Admin:** "When a **Contact** raises a **Ticket**, do we need **Sign-off** to close it?"
> **Manager:** "Only for billable work — internal fixes just need manager approval."

## Flagged ambiguities

- "approval" was used to mean both manager approval and **Sign-off** — resolved: these are distinct.
```

## Rules

- **Be opinionated.** When several words mean the same thing, pick the best one and list the rest as aliases to avoid.
- **Flag conflicts explicitly.** If a term is used two ways, call it out under "Flagged ambiguities" with a clear resolution.
- **Keep definitions tight.** One sentence. Define what the term IS, not the steps around it.
- **Show relationships.** Use bold term names and express how many relate to how many where it's obvious.
- **Only include terms specific to this work.** Everyday office words that everyone already agrees on don't belong. Before adding a term, ask: is this a word the team uses in a particular way here, or just a normal word? Only the former belongs.
- **Group terms under subheadings** when natural clusters appear (e.g. People, Documents, Statuses). A flat list is fine if everything sits in one area.
- **Write an example dialogue.** A short exchange between two roles that shows the terms used naturally and clarifies the boundaries between related ones.
- **Do not invent filler.** Add relationships, example dialogue, and flagged ambiguities only when the session produced useful content for them.
