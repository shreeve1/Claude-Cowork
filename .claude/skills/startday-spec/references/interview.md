# Interview

Ask these through `talk-it-through`, one at a time, each with your recommended answer. Skip any the owner already answered, and skip a module's questions when the owner did not pick it. Stop early when the rest have obvious defaults, and state the default you used.

A blank or vague answer counts as not answered (core rule 6). Ask again once, then use the recommended default and say so.

## Questions

1. **What should feed your day?** Pick any mix of the modules in `modules.md`: work items you drive to completion, meeting transcripts, files or pages to watch. A weekly look-back is also on offer: it saves a lesson only when you taught it more than once.
   Recommend: work items plus meetings; add watch targets when there is a page or folder you check by hand today; add the look-back after two or three weeks of use, when there is something to look back on.

2. **Work items: what is one, and where do they come from?** Tickets, email threads, tasks, projects? Which tool or connector holds them, and can your agent already read it here?
   Recommend: the thing you already track to completion, from the one source you check first every morning.

3. **Work items: which are yours today?** Assigned to you, flagged, due soon, in one list? Anything to always skip?

4. **Meetings: where do transcripts land?** The folder your transcription tool saves or syncs to. Open one with the owner to confirm it is plain text the agent can read.
   Recommend: one folder for all transcripts, outside the research folder.

5. **Watch: what should be watched, and why?** Each folder, file or page, with one line on what change matters. Pages must load without signing in.

6. **Working hours and timezone?** When should the day start, and when should it stop starting new research?
   Recommend: stop new research an hour before your day ends.

7. **What does "done for the day" mean?** A time, an empty list, or both? What summary do you want at the end?

8. **What may the agent read?** Mail, calendar, files, the web, other systems? Anything strictly off limits?

9. **What counts as a change needing your approval?** List the actions you care about (replies, closing items, moving files, booking time). Everything else that writes or sends is a change too.
   Recommend: anything that sends, deletes, moves, books or edits outside the research files.

10. **Where should research files, the approvals page and the activity log live?** A folder in this workspace, a notes app, a shared drive?
    Recommend: one folder in this workspace, one file per item, plus one approvals page and one activity log.

11. **How do you want to be told something needs you?** Desktop notification, chat message, email to yourself, or just the approvals page?
    Recommend: just the approvals page until the loop has run a few days.

12. **How should it run during the day?** Show the table in `runners.md` and ask which agent app this machine runs. Then pick a runner and an interval.
    Recommend: no runner for the first days (type `startday` yourself), then the local scheduled task of the app you use, every 15 minutes.

13. **Anything that must never happen?** People never to contact, items never to touch, times never to send.

## After the interview

Restate the answers as a short list. Ask "Is anything here wrong?" Fix it, then fill in `skeleton-SKILL.md` and write `.claude/startday.json`:

```json
{
  "research_folder": "<folder>",
  "approvals_page": "<path>",
  "activity_log": "<path>",
  "watch": [
    {"path": "<transcripts folder>", "use": "meetings", "why": "meeting transcripts"},
    {"url": "<page>", "why": "<what change matters>"}
  ]
}
```

Leave `watch` as `[]` when neither Meetings nor Watch was picked. Add `.claude/startday.state.json` to `.gitignore`.
