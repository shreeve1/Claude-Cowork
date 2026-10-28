---
name: "drawio"
description: "Draw and edit draw.io diagrams (.drawio files) with the owner, taking turns. You edit the file in the workspace and open it in draw.io in the app's built-in browser pane (with a link as backup); they change it and save it back. Use when the owner asks for a diagram or flowchart they can edit themselves, wants to sketch or brainstorm a flow, workflow, process, agent or bot design, or system structure, mentions draw.io or drawio, or when reading or editing any .drawio file. Use excalidraw-diagram instead when they ask for Excalidraw."
---

# drawio

The owner drags shapes in draw.io in the app's built-in browser pane; you read and edit the same `.drawio` file in the workspace. You take turns. The file is the shared state. Nothing runs in the background and nothing needs installing: each of your turns ends with the current file open in draw.io (plus a link to it), and the owner saves it back to the file when they are done.

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

After every change, open the diagram for the owner yourself; don't leave them only a link to click. Make the link and a preview page:

```bash
python3 <skill-dir>/scripts/link.py <sandbox path of the .drawio file> --html <workspace>/artifacts/diagrams/previews/<preview name>.html
```

`<skill-dir>` is the folder this SKILL.md was loaded from; if you don't know it, use `.claude/skills/drawio` in the workspace. `<workspace>` is the workspace's sandbox path. `<preview name>` is the diagram's workspace-relative path without `.drawio`, with `/` turned into `-`: `memory/docs/topic.drawio` gives `memory-docs-topic.html`. Previews never go in `memory/`. It prints the link, which opens app.diagrams.net with the diagram in it, named after the file. The whole diagram is inside the link after `#`, which the browser keeps to itself, so nothing is uploaded. It needs internet.

Then, in this order:

1. **Open the link in the built-in browser pane, and make it the last thing you show.** The side panel shows one thing at a time, so whatever you open last is what the owner sees. Use the built-in browser tools (`mcp__Claude_Browser__*`; load them via ToolSearch if deferred):
   - **First time this session:** `preview_start` with the link as `url`. Remember the `tabId` it returns.
   - **Later turns:** `navigate` that same `tabId` to the new link (pass `force: true` only if the owner has said they saved, since it discards unsaved draw.io edits). Don't open a second tab: an old tab left open can save over your changes.
   - Call `tabs_context` afterwards. If it says the pane is hidden, ask the owner to bring it back (Ctrl+Shift+B on Windows, Cmd+Shift+B on Mac, or the globe icon).
   - If the built-in browser is unavailable, use Claude in Chrome the same way (new tab the first time, same tab after). If neither is available, rely on the link in step 3.
2. **Don't put the preview page in the side panel.** Write it with `--html` as a fallback, but don't call `present_files` on it (that would cover the draw.io tab). Mention its path only if the browser couldn't open the link.
3. **Give the link** in your message as well, as a clickable link, and the file's full Windows path (the workspace folder plus the relative path), which they need to save it back.

If `link.py` says the link is too long (a very large diagram), give the Windows path instead: they open app.diagrams.net in a new tab, choose **Open Existing Diagram** and pick the file.

**Saving it back.** In draw.io the owner presses **Ctrl+S**, sets **Where** to **Device**, clicks **Save**, picks the file at that Windows path and agrees to replace it. Each new link needs this once, because its tab isn't connected to the file yet; after that, Ctrl+S in the same tab saves straight to the file. Spell the steps out until they've done it a few times. If Save downloaded a copy instead, ask them to save it over the file at that path, or tell you where the copy is.

The owner can also use the draw.io desktop app if they have it: double-click the file in File Explorer. If its **File > Autosave** is ticked, a window left open can write over your changes; suggest unticking it.

## Taking turns

1. **Their turn ends when they save.** When the owner says they updated, changed or edited the diagram, take that as saved: read the file at once and don't ask again. If you need to edit an existing diagram and they haven't said, ask them to save first. A new diagram has nothing to save.
2. **Say what they changed** since your last turn, in a line or two (added, moved, relabelled, deleted), because that is their half of the conversation. If the file hasn't changed since your last turn, their save didn't reach it: walk them through **Saving it back**.
3. **Edit**, following `reference/format.md`.
4. **Tell them** what you changed, and open the new version as **Opening a diagram** says. Reuse the same browser-pane tab; any other draw.io tab they still have open on this diagram, they close: saving from it would overwrite your changes. (Desktop app: close the window and reopen the file instead of using the link.)
5. If they did save over your changes, read the file, tell them which of your changes are gone, and redo them on top of theirs. Diagrams under `artifacts/` have no git history, so keep your own changes in mind until the owner has the new version open.

Before writing or editing any `.drawio` XML, read [`reference/format.md`](reference/format.md).

## Question and decision notes

Use notes for the whole life of a diagram, not only while brainstorming:

- Keep a clear column on the right for open questions, decisions to confirm, assumptions and risks the owner can answer or correct. Keep the main flow or structure separate from it. Stack active notes there, short and specific, in the yellow note style from `reference/format.md`.
- When a question is answered, keep its note as history: mark it answered, move it below the active notes, or gather answered notes into one "Answered decisions" note. Don't delete a note just because it's resolved.
- Add new questions to the active column as they come up, and update the notes in the same turn a decision is settled.

## Kick-off: "let's talk about X and brainstorm"

When the owner asks for this skill with a subject to talk about, that is a yes to the diagram. First run **Find before create**. Your first message either asks them to confirm an existing diagram or gives them a new seed diagram to react to:

1. **Follow the `talk-it-through` skill** for the conversation. The diagram is its visual companion: this replaces that skill's visual companion offer and its Mermaid diagram, because the canvas is the diagram. Everything else in that skill still applies.
2. **Look before you draw.** Read what the subject points at: the notes, documents or earlier conversation it names or that obviously relate to it. Stop once you can sketch how it works today, or what they seem to want. With little or nothing to read, seed from the subject alone: a topic map of the usual parts of such a thing, mostly `?` labels, beats a blank page.
3. **Pick the shape** that fits:
   - **Flow** (steps, a process, a bot or agent loop, a request path): a rough flowchart of what you know.
   - **Structure** (a system, its parts and how they connect): boxes for the parts, arrows for the connections.
   - **Topic map** (anything still fuzzy: an idea, a decision, a problem): the subject in the centre, branches for the parts, goals, constraints and options.
4. **Seed it:** 5 to 12 main shapes, labelled in the owner's words. Anything you filled in yourself ends its label with a space and a question mark ("Agent triages ?"). Add 2 to 4 yellow notes (200×80) in the question column for the open questions whose answers would change the diagram most. Save it where **Where diagrams go** says, named after the subject, and check the XML.
5. **First message:** the link and the path (see **Opening a diagram**); a line or two on what you drew and what you based it on; then the `talk-it-through` first message (a one-line subject counts as underspecified, even when the files you read fill in a lot), ending with its single question, which the owner can answer in chat or on the diagram, whichever is quicker.

From then on, follow **Taking turns**.

## While brainstorming or planning

- When a flow, a sequence of steps, a set of states or a structure comes up, offer to sketch it in a message of its own instead of describing it. If they already asked for a diagram, skip the offer and follow **Find before create**.
- Sketch the current understanding: rough, labelled, few shapes. Put each open question or guess in a yellow note beside the step it concerns.
- Keep the diagram in step with the conversation: when they settle something in chat, update the diagram in the same turn and say so.
- Read their edits as answers. A deleted box is a rejected step; a new arrow is a dependency they care about. Confirm what you read before building on it.
- Decisions belong in the note or document the diagram illustrates; the diagram shows them. Link the diagram from that note or document.
