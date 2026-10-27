---
name: drawio
description: Draw and edit draw.io diagrams (.drawio files) with the owner, taking turns. You edit the file in the workspace and give them a link that opens it in draw.io in their browser; they change it and save it back. Use when the owner asks for a diagram or flowchart they can edit themselves, wants to sketch or brainstorm a flow, workflow, process, agent or bot design, or system structure, mentions draw.io or drawio, or when reading or editing any .drawio file. Use excalidraw-diagram instead when they ask for Excalidraw.
---

# drawio

The owner drags shapes in draw.io in their browser; you read and edit the same `.drawio` file in the workspace. You take turns. The file is the shared state. Nothing runs in the background and nothing needs installing: each of your turns ends with a link that opens the current file in draw.io, and the owner saves it back to the file when they are done.

## Where diagrams go

A path the owner names wins. Otherwise place each diagram beside what it illustrates, with the same basename, using the first match:

- **A memory note:** use the `personal-memory` skill to find or create the related note, save the `.drawio` beside it, and add a relative link from the note to the diagram. For example `memory/docs/topic.md` gets `memory/docs/topic.drawio`.
- **A document in the workspace** (a report, a plan, a client document): beside that document, for example `clients/<short>/projects/migration.md` gets `migration.drawio`.
- **Anything else:** `artifacts/diagrams/<subject>.drawio`.

The extension is `.drawio`.

## Find before create

Reuse the relevant diagram instead of creating a second one:

1. Search the chosen location and the workspace for `.drawio` files matching the subject, the document's or note's basename, or an obviously related name.
2. If one exists, give its path (or each path) and ask the owner to confirm which to use. Don't create or edit a diagram until they confirm.
3. If none exists, create one at the chosen location.

## Opening a diagram

After every change, make the link and give it to the owner as a clickable link:

```bash
python3 <skill-dir>/scripts/link.py <sandbox path of the .drawio file>
```

`<skill-dir>` is the folder this SKILL.md was loaded from; if you don't know it, use `.claude/skills/drawio` in the workspace. The link opens app.diagrams.net in their browser with the diagram in it, named after the file. The whole diagram is inside the link after `#`, which the browser keeps to itself, so nothing is uploaded. It needs internet. Also give the file's full Windows path (the workspace folder plus the relative path), which they need to save it back.

If `link.py` says the link is too long (a very large diagram), give the Windows path instead: they open app.diagrams.net in a new tab, choose **Open Existing Diagram** and pick the file.

**Saving it back.** In draw.io the owner presses **Ctrl+S**, sets **Where** to **Device**, clicks **Save**, picks the file at that Windows path and agrees to replace it. Each new link needs this once, because its tab isn't connected to the file yet; after that, Ctrl+S in the same tab saves straight to the file (Edge or Chrome). Spell the steps out until they've done it a few times. If Save downloaded a copy instead, ask them to save it over the file at that path, or tell you where the copy is.

The owner can also use the draw.io desktop app if they have it: double-click the file in File Explorer. If its **File > Autosave** is ticked, a window left open can write over your changes; suggest unticking it.

## Taking turns

1. **Their turn ends when they save.** When the owner says they updated, changed or edited the diagram, take that as saved: read the file at once and don't ask again. If you need to edit an existing diagram and they haven't said, ask them to save first. A new diagram has nothing to save.
2. **Say what they changed** since your last turn, in a line or two (added, moved, relabelled, deleted), because that is their half of the conversation. If the file hasn't changed since your last turn, their save didn't reach it: walk them through **Saving it back**.
3. **Edit**, following `reference/format.md`.
4. **Tell them** what you changed and give the new link. They close their old draw.io tab first: saving from it would overwrite your changes. (Desktop app: close the window and reopen the file instead of using the link.)
5. If they did save over your changes, read the file, tell them which of your changes are gone, and redo them on top of theirs. Diagrams under `artifacts/` have no git history, so keep your own changes in mind until the owner has the new version open.

Before writing or editing any `.drawio` XML, read [`reference/format.md`](reference/format.md).

## Question and decision notes

Use notes for the whole life of a diagram, not only while brainstorming:

- Keep a clear column on the right for open questions, decisions to confirm, assumptions and risks the owner can answer or correct. Keep the main flow or structure separate from it. Stack active notes there, short and specific, in the yellow note style from `reference/format.md`.
- When a question is answered, keep its note as history: mark it answered, move it below the active notes, or gather answered notes into one "Answered decisions" note. Don't delete a note just because it's resolved.
- Add new questions to the active column as they come up, and update the notes in the same turn a decision is settled.

## Kick-off: "let's talk about X and brainstorm"

When the owner asks for this skill with a subject to talk about, that is a yes to the diagram. First run **Find before create**. Your first message either asks them to confirm an existing diagram or gives them a new seed diagram to react to:

1. **Follow the `brainstorm-idea` skill** for the conversation; the diagram is its visual side.
2. **Look before you draw.** Read what the subject points at: the notes, documents or earlier conversation it names or that obviously relate to it. Stop once you can sketch how it works today, or what they seem to want. With little or nothing to read, seed from the subject alone: a topic map of the usual parts of such a thing, mostly `?` labels, beats a blank page.
3. **Pick the shape** that fits:
   - **Flow** (steps, a process, a bot or agent loop, a request path): a rough flowchart of what you know.
   - **Structure** (a system, its parts and how they connect): boxes for the parts, arrows for the connections.
   - **Topic map** (anything still fuzzy: an idea, a decision, a problem): the subject in the centre, branches for the parts, goals, constraints and options.
4. **Seed it:** 5 to 12 main shapes, labelled in the owner's words. Anything you filled in yourself ends its label with a space and a question mark ("Agent triages ?"). Add 2 to 4 yellow notes (200×80) in the question column for the open questions whose answers would change the diagram most. Save it where **Where diagrams go** says, named after the subject, and check the XML.
5. **First message:** the link and the path (see **Opening a diagram**); a line or two on what you drew and what you based it on; then one question, which the owner can answer in chat or on the diagram, whichever is quicker.

From then on, follow **Taking turns**.

## While brainstorming or planning

- When a flow, a sequence of steps, a set of states or a structure comes up, offer to sketch it in a message of its own instead of describing it. If they already asked for a diagram, skip the offer and follow **Find before create**.
- Sketch the current understanding: rough, labelled, few shapes. Put each open question or guess in a yellow note beside the step it concerns.
- Keep the diagram in step with the conversation: when they settle something in chat, update the diagram in the same turn and say so.
- Read their edits as answers. A deleted box is a rejected step; a new arrow is a dependency they care about. Confirm what you read before building on it.
- Decisions belong in the note or document the diagram illustrates; the diagram shows them. Link the diagram from that note or document.
