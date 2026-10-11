# Core rules

These six rules are fixed. Every owner's `startday` keeps them word for word. The interview can change what an item is, where it comes from and how the loop runs, but never these.

## The rules

1. Research is READ-ONLY. The loop gathers and prepares. It never changes anything in the owner's systems.
2. Every change is an APPROVAL the human ticks: a checkbox in a document the human reads. A change is executed only after the tick.
3. The loop NEVER blocks waiting on the human. It parks the item, moves on, and re-checks later.
4. Each work item gets its own research file with a section named "Path to Close" that says what is still needed to finish the item.
5. The human's edits always survive. The loop never overwrites text the human typed.
6. Empty or blank answers count as not answered.

## What each rule means in practice

**1. Read-only research.** Reading mail, tickets, calendars, files and web pages is fine without asking. Sending, replying, moving, deleting, closing, assigning, booking, paying or editing anything outside the research files is a change. If unsure whether something is a change, treat it as one.

**2. Approvals.** Each approval is one line with a checkbox, a short title, the exact target (who or what it changes) and the exact text or action, in a document the owner reads (for example `Approvals.md`):

```
- [ ] A-012 Reply to the supplier about the late order
  Target: supplier email thread "Order 5521"
  Body: <the exact text that will be sent>
```

- `[x]` means yes. The loop executes exactly what is written: same target, same text.
- `[-]` followed by a reason means no. The loop records the reason and does not draft it again.
- If the owner edited the body, the loop asks once "Send your edited version?" before using it.
- If the item changed since the draft (a new reply arrived), the approval is stale: cancel it and draft a fresh one.
- After executing, check that the change actually happened, then mark the line done with the time. If it failed, say so on the line.

**3. Never wait.** Anything only the owner can supply becomes a question in the research file or a "Needs you" line (sign-ins, phone codes, clicks). Then the loop moves to the next item. Each turn it re-checks parked items for an answer, a tick or new activity.

**4. Research file and Path to Close.** One file per item, in the folder the owner chose. It holds a short header (item id, title, source, status), a "Path to Close" section, dated findings (newest first), questions and the approvals drafted for it. Path to Close is rewritten each time research advances; it lists the remaining steps, who owns each one, and the next approval id.

**5. Owner's text survives.** The loop writes only to its own sections. It never rewrites, reorders or deletes lines the owner typed, including answers and notes. If the owner's text conflicts with research, the owner's text wins and research notes the conflict.

**6. Blank is not an answer.** An empty `Answer:` line, a lone dash, "?", or whitespace means the question is still open. The loop never invents an answer to fill a blank.

## Where things end up

- A work item stops when research hits a wall: the next step is a change (drafted as an approval), needs a person, or needs a sign-in. Record the wall in the research file and move on.
- Never put passwords or other secrets in any file. Say where they live instead.
- Notifications say that something needs the owner, not the private details.
