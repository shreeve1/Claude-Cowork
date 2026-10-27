---
name: meeting
description: Process the meeting transcripts waiting in the owner's transcripts folder. For each one it files lasting facts to memory, adds progress to the matching work item, drafts follow-ups for the owner to approve, writes a meeting record, then archives the transcript. Use when the owner says "meeting", "process my meetings" or "process the last meeting", or names the attendees, person, company or work item a meeting was about. startday's Meetings module runs it too.
---

# Meeting

Turn each waiting transcript into filed facts and one meeting record, then move it to the archive. A meeting only extracts. Nothing is sent or changed outside this workspace: every follow-up is a draft the owner approves.

## Settings

Read `memory/preferences/meetings.md` first. It holds this owner's transcripts folder, archive folder, record folder, their name, what counts as a work item, and anything they want always or never filed. If the note is missing, or the folder there does not exist, run "First use" below before anything else.

Script: `python3 .claude/skills/meeting/scripts/meetings.py --folder <transcripts folder> [--archive <archive folder>] <list | show KEY | archive KEY>`, run from the workspace root. It reads `.txt`, `.md`, `.vtt`, `.srt`, `.json` and `.docx`, and treats a subfolder as one meeting. Only `archive` writes. Without Python, do by hand what it does: list the folder newest first, skipping names starting with `.` and the archive folder. A subfolder is one meeting; read every transcript file in it. A meeting is done when a record in the record folder has `source:` equal to its name; it changed when the file is newer than that record's `date`. Skip a meeting changed in the last two minutes. Open `.vtt` and `.srt` files as text and ignore the timing lines. Move a processed file into the archive folder, adding ` (2)` before the extension when the name is taken. `.docx` needs Python or the owner pasting the text.

## Inputs (all optional)

- Which meeting: a key or file name from `list`, a path, or "last" (the newest).
- Who attended.
- The person, company or work item it was about.
- A few words on what the meeting was.

What the owner says outranks inference. A named person or work item is the filing target. If the transcript disagrees, say so in chat and ask before filing.

## Steps

1. **Pick meetings.** Run `list`. Work the items with `record: null`, newest first, at most 5 (name the rest in the reply). With a key, path or "last", work only that one. Skip items with `settling: true`: the tool may still be writing them. Skip items with `words: 0`: tell the owner nothing readable was found, and archive nothing. An item with `same_name_record` was processed before and has changed since: update that record instead of writing a second one. An item with `same_text_record` has the same text as a meeting already done under another name (a copy or re-export): ask the owner before processing it, and archive it once they confirm it is a duplicate. _Done when:_ each listed item is chosen or skipped, with a reason for every skip.

2. **Read.** Run `show <key>` and read the whole transcript. A summary the transcription tool wrote is a hint: check each claim against the transcript and drop what it does not support. Load `memory/glossary.md`, and the hub of any person or thing you track (the "Work on one" row of `memory/rules.md`) that the transcript names. _Done when:_ the whole transcript is read.

3. **Who it was with.** Use the owner's input first. Without it, a calendar event overlapping the meeting's time is a guess; check it when a calendar is readable (startday's Calendar module, or a calendar connector). Confirm a person, company or tracked thing only when the owner named it, or the transcript names it, one of its people from the glossary, or one of its work items. Otherwise it is unconfirmed. _Done when:_ the meeting is confirmed, internal (only the owner's own people), or unconfirmed with its best guess.

4. **Find the work items.** List the work items the meeting discusses (the meetings note says what a work item is: a ticket, a project, a task, an email thread). Find each one's research file or note. With startday set up, use its research folder from `.claude/startday.json`. _Done when:_ every work item the meeting touches has a file, or is marked "no file".

5. **Sort and file.** Put every useful item in one home:
   - A lasting fact about a person or thing you track (setup's tracking model; skip this line if the owner tracks none): Client Memory, through the `personal-memory` skill. One fact per note, `source: "meeting <record name>"`, existing notes updated in place.
   - Any other lasting fact, rule or preference the owner stated: memory, through `personal-memory` capture.
   - Progress, a decision or an answer on a work item: that item's research file, as a dated finding.
   - A change outside this workspace (an email, a booked time, a closed task, a message): a drafted approval. With startday set up, draft it on the item's research file in startday's approval format. Otherwise, list it in the reply in full text and do it only after the owner's yes.
   - A question only the owner can answer: a question in the record, one sentence with an empty `Answer:` line.
   - The owner's own promises: the record's commitments. Other people's promises: the record's action items.
   - A repeatable step list: offer it as a procedure. Do not write it here.
   With an unconfirmed person or company, keep their facts in the record's "Held facts" and ask `Is the meeting on <date> about <name>?`. Nothing goes to Client Memory until it is answered. _Done when:_ every useful item has a home or is held, and nothing is filed from a tool summary alone.

6. **Write the meeting record** in the record folder (see "Record"). A meeting with nothing worth saving (a test, small talk) gets no record. Say so in the reply. _Done when:_ the record exists with a link for every filed item, or the reply says why none was needed.

7. **Archive.** Run `archive <key>`. It refuses a meeting still being written and never overwrites: a second file with the same name gets ` (2)`. Archive a meeting without a record too, once the owner has seen why. If startday watches the transcripts folder and the archive sits inside it, the move shows up there as a gone file; that is expected. _Done when:_ each processed meeting is in the archive folder, or its refusal is reported.

8. **Report.** For each meeting, in chat: title and time, who it was with (or the open question), then one line per filed item with its path. Show every drafted follow-up and question in full text, so the owner can approve or answer in chat. Commit per `CLAUDE.md`: the record, the files you wrote, and the memory notes. Transcripts and the archive stay out of git unless the meetings note says otherwise. _Done when:_ every processed meeting is in the reply.

## Record

File: `<record folder>/<YYYY-MM-DD>-<short-topic>.md`. Without a record folder in the meetings note, use `notes/meetings/` or, for a confirmed client, `<client_folder>/<short>/meetings/` (folder map: `memory/preferences/document-scaffolding.md`).

```markdown
---
type: meeting-record
source: <transcript file or folder name, as `list` shows it>
transcript_hash: <from list>
date: <YYYY-MM-DD HH:MM>
with: [<short names, confirmed only>]
guess: <best guess while unconfirmed, else null>
---

# <Topic> - <date> (<attendees>)

## Summary
## Decisions
## Facts saved
## Work item updates
## Follow-ups drafted
## My commitments
## Action items (others)
## Held facts (not yet confirmed)
## Questions
```

Omit an empty section. `source` and `transcript_hash` stay exact: `list` uses them to tell which meetings are done.

## First use

Ask these one at a time, each with the recommended answer, then save the answers to `memory/preferences/meetings.md` with `personal-memory`:

1. **Where do your transcripts land?** The folder the transcription tool (Teams, Zoom, Otter, Granola, a recorder app) saves or syncs to. Run `list` on it together and open one to check it reads as text. Recommend: one folder for all transcripts, outside the research folder.
2. **Where should processed transcripts go?** Recommend: `Archive` inside that folder.
3. **Where should meeting records go?** Recommend: `notes/meetings/`, and the client's own `meetings/` folder when one is confirmed.
4. **What is a work item for you, and where do you keep them?** Recommend: whatever startday tracks; without startday, the notes or tool you check first each morning.
5. **Anything always or never to file?** People to leave out, topics that never go to memory, a tool summary to ignore.

With startday set up, also offer to add the Meetings module (`startday-spec`, `references/modules.md` "Meetings"), so new transcripts are processed during the day.
