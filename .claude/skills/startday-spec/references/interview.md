# Interview

Ask these through `talk-it-through`, one at a time, each with your recommended answer. Skip any the owner already answered, and skip a module's questions when the owner did not pick it. Stop early when the rest have obvious defaults, and state the default you used.

A blank or vague answer counts as not answered (core rule 6). Ask again once, then use the recommended default and say so.

## Start with the morning

0. **Walk me through how your day starts today.** What do you open first, what do you check, what do you decide? Listen for the calendar, the lists and the inboxes they name; those answers pre-fill the questions below, so skip what they already covered. Naming a calendar never skips the read test in question 1.

## Calendar (asked first: most days start from it)

Calendar is included unless the owner says no or no calendar can be read here; then skip questions 2 to 5.

1. **Where is your calendar, and can your agent read it here?** Google, Outlook or Microsoft 365, iCloud, a shared calendar link, more than one? Always read today's events together now to prove it, even when question 0 named the calendar, and check the times show in the owner's timezone.
   Recommend: the one calendar your meetings are booked in. If none can be read here, leave Calendar out and say so; the other modules still work.

2. **Which events fix your day, which can move, and which should be ignored?** Fixed: a time you must be there (with other people, a call, a site visit). Flexible: your own blocks and placeholders, worked whenever fits. Ignored: declined events, all-day reminders, personal events, anything else named.
   Recommend: events with other attendees are fixed; events only you attend are flexible; declined and all-day events are ignored.

3. **Which fixed events get a brief, and how early?** A meeting brief: who is coming, why (from the invite), the work items it touches, notes from the last meeting with these people, open questions, what you promised them.
   Recommend: a one-screen brief 30 minutes before each fixed event with other attendees. Write the answer as the Brief rule; the module briefs exactly those events.

4. **What should happen after a meeting?** Follow-ups drafted for your approval, a question asking what came out of it, nothing?
   Recommend: draft follow-ups from the transcript when Meetings is picked; otherwise, at the event's end, ask one question on the linked work item's research file (on the activity log when no item is linked): "Anything to follow up from <event>?"

5. **Should the day end with a look at tomorrow?**
   Recommend: yes, list tomorrow's fixed events before midday in the wrap-up.

## What else feeds the day

6. **What else should feed your day?** Pick any mix of the modules in `modules.md`: work items you drive to completion, meeting transcripts, files or pages to watch. A weekly look-back is also on offer: it saves a lesson only when you taught it more than once.
   Recommend: work items; add meetings when a transcription tool already saves transcripts to a folder; add watch targets when there is a page or folder you check by hand today; add the look-back after two or three weeks of use.

7. **Work items: what is one, and where do they come from?** Tickets, email threads, tasks, projects? Which tool or connector holds them, and can your agent already read it here?
   Recommend: the thing you already track to completion, from the one source you check first every morning.

8. **Work items: which are yours today?** Assigned to you, flagged, due soon, in one list? Anything to always skip?

9. **Meetings: where do transcripts land?** The folder your transcription tool saves or syncs to. Use the one already in `memory/preferences/meetings.md` when it is set; otherwise run the `meeting` skill's "First use" questions now, which save it there. Open one transcript with the owner to confirm it reads as text.
   Recommend: one folder for all transcripts, outside the research folder.

10. **Watch: what should be watched, and why?** Each folder, file or page, with one line on what change matters. Pages must load without signing in.

## How the day runs

11. **Working hours and timezone?** When should the day start, and when should it stop starting new research?
    Recommend: start 30 minutes before your first fixed event or your usual start, whichever is earlier; stop new research an hour before your day ends.

12. **What does "done for the day" mean?** A time, an empty list, or both? What summary do you want at the end?

13. **What may the agent read?** Mail, calendar, files, the web, other systems? Anything strictly off limits?

14. **What counts as a change needing your approval?** List the actions you care about (replies, closing items, moving files, accepting or declining invites, booking time). Everything else that writes or sends is a change too.
    Recommend: anything that sends, deletes, moves, books, accepts, declines or edits outside the research files.

15. **Where should research files, the approvals page and the activity log live?** A folder in this workspace, a notes app, a shared drive?
    Recommend: one folder in this workspace, one file per item, plus one approvals page and one activity log.

16. **How do you want to be told something needs you?** Desktop notification, chat message, email to yourself, or just the approvals page?
    Recommend: just the approvals page until the loop has run a few days.

17. **How should it run during the day?** Show the table in `runners.md` and ask which agent app this machine runs. Then pick a runner and an interval.
    Recommend: no runner for the first days (type `startday` yourself), then the local scheduled task of the app you use, every 15 minutes.

18. **Anything that must never happen?** People never to contact, items never to touch, times never to send.

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
