# Adaptation list

The skeleton says what each run does. This list fits it to the owner's harness and machine. Find out, adapt, and write down what was chosen.

The owner must verify the loop on a test system (or a test list of items that cannot reach real people) before a first real day.

## Find and adapt

1. **Runner.** Pick one from `runners.md` and follow its "Before trusting a runner" steps. If the app the owner uses is not listed, use "None" until its scheduler is tested the same way.

2. **Local reach.** The runner must see this workspace and the owner's MCP config. Python is needed only for `watch.py`, the change detection for Meetings and Watch. Without Python those two modules use the by-hand method in `modules.md` "Watching without Python": less exact, more tokens per run, so tell the owner. Look-back and memory notes need no script (`personal-memory` has a no-Python path). Test a run writes a file here before anything else.

3. **Notification mechanism.** How a message reaches the owner on this machine: desktop notification, chat, email to self, or only the approvals page. Test that one arrives. Keep private details out of it.

4. **Timezone.** The machine's clock and the owner's working timezone may differ. Find both and use the owner's for Hours. Scheduled tasks use the machine's local time.

5. **Connectors and sign-ins.** Confirm the agent can read each source with the owner's existing access. Note any sign-in that expires and how the run reports it (a needs-you line, never a wait). A scheduled run cannot answer a sign-in prompt.

6. **Permissions.** Scheduled runs stall on permission prompts. On the first manual run, allow each tool and command the run needs ("always allow"), and nothing broader.

7. **File locations.** Confirm the research folder and approvals page are somewhere the owner actually reads, and that the owner's editor saves the checkbox tick in a way the agent can see.

8. **Stopping.** Confirm how the owner stops the loop at once if something looks wrong (from `runners.md`).

## Before a first real day

- Run one full day on the test system: gather, research, draft, tick one approval, execute it, reject one, wrap up.
- Check rule 5 directly: type a note and an answer in a research file, run a turn, and confirm both are untouched.
- With Calendar picked: book a test event with another attendee inside the brief lead time, run a turn, and confirm the day plan lists it as fixed and its brief appears. Move it and confirm the next run updates the day plan once. Book one for tomorrow morning and confirm the wrap-up lists it.
- With Meetings picked: drop a test transcript into the folder, wait two minutes and one run, and confirm a meeting record appears and the transcript moved to the archive folder. Run once more and confirm nothing is reprocessed.
- With Watch picked: change a watched file, confirm the next run reports it once and the run after reports nothing.
- With Look-back picked: plant three rejections on three different items, each with the same reason in the owner's words. Run it and confirm one memory note is written, listing those three items as its source, with a `memory/rules.md` row that reaches it. Then plant five agent-written voids from one cause (for example `superseded: tone rule`) with no owner feedback, run it again, and confirm it writes only a candidate line in the activity log.
- With Look-back picked, also check the window: plant one rejection on one item, run it (a candidate line, no note). Run it again a week later with the same rejection still there and confirm it is not counted twice, then add two more on other items and confirm the note is written.
- Only then point it at real items.
