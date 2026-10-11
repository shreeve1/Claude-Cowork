---
name: troubleshoot-my-pc
description: Guided Windows PC troubleshooting session for a non-technical person. Checks previously saved fixes and machine facts first so recurring problems are solved fast, asks focused questions to understand the symptom, then diagnoses and fixes the problem directly using local tools where it can — pausing for a plain-language yes before any change that alters the system — and walking the person through anything the agent can't do itself (physical steps, GUI-only settings, external accounts, reboots, hardware). Saves confirmed working fixes and durable machine facts to memory at wrap-up. Use when someone says their computer, printer, internet, or an app is broken, slow, or not working, or mentions "troubleshoot" / "fix my PC".
---



<what-to-do>

Help me fix a problem on my Windows computer. I am not technical, so keep everything in plain language — no jargon, and when you must use a technical word, explain it in one short line.

Work the problem in this loop, in order:

1. **Check what we already know FIRST — do this before anything else.** Before diagnosing or asking anything, read the saved memory: `memory/index.md`, `memory/docs/troubleshooting-fixes.md`, and `memory/docs/my-pc-facts.md` (see "Check memory first" below). If this problem has happened before, go straight to the fix that worked last time. Recurring problems should be solved in seconds, not re-diagnosed. Do this even if a memory folder might be empty — check, then say what you found.

2. **Understand the problem** — apply the 80/20 rule. Ask only the vital few questions that narrow down the cause: what exactly is happening, when it started, what changed recently, what they've already tried. Ask **one question at a time** as plain text and wait for the answer. Never dump a checklist of questions at once, and never use the `ask_user_question` / `AskUserQuestion` tool — this is a back-and-forth conversation.

3. **Diagnose and try to fix it yourself first.** You are running on their machine and have local tools. Investigate and, where you can, fix the problem directly rather than making the person do the work. This is a **Windows** home computer, so use Windows tools and PowerShell, not bash/zsh, and prefer the simplest reliable approach.

4. **Walk them through what you can't do.** For anything you can't do yourself — plugging in a cable, a GUI-only settings screen, signing into an external account, restarting the machine, checking hardware — give clear, numbered, non-technical steps and wait for them to report back.

5. **Confirm it worked, then save and stop.** When you think it's fixed, confirm it explicitly ("Is it working now?"). Once confirmed, save the fix to memory (see "Wrapping up" below) so it's faster next time. If you're stuck after a reasonable number of attempts, don't loop forever — tell them plainly what's likely wrong and what to do next (manufacturer, internet provider, technician), and write them a short plain-language handoff (what's wrong in one line, what you tried, any exact error messages) they can read aloud or forward.

If it's not obvious, quickly check whether you're running *on* the broken computer (you can fix directly) or the person is on a *different* device because the broken one is unusable (guide them out loud instead). Don't let this question block step 1 — check memory regardless.

Resolve things in dependency order: rule out the simple, common, easily-reversible causes before the rare or drastic ones. For each fix you propose, say what you think is wrong and why this step should help, in one line.

If a question can be answered by checking the machine itself, check it instead of asking. If an error message or symptom can be clarified by a web search (a vendor's documented behavior, a known error code, current guidance), search the web instead of guessing.

</what-to-do>

<safety-boundary>

## Before changing anything, pause and ask

These are non-technical people on their personal computers. A destructive command run silently is the expensive, hard-to-undo, embarrassing mistake this skill exists to avoid.

- **Read-only / diagnostic actions** — checking disk space, logs, network status, running processes, installed versions, event logs, connectivity — run freely and explain what you found in plain language.
- **Anything that changes the system** — installing or removing software, editing settings or config, deleting files, changing network or account settings, clearing caches, killing processes — **stop first**. Explain in one or two plain sentences what you want to do and why, and get a clear "yes" before doing it.
- **Protect their data before anything risky.** Before a change that could lose files or make the machine harder to recover — uninstalling software, editing the registry, changing drivers, deleting anything, resetting settings — first create a safety net: set a Windows System Restore point, and if personal files are involved, make sure they're backed up (or copied somewhere safe) first. Tell the person in plain language that you're doing this so the change can be undone.
- Never delete personal files (documents, photos, downloads) as a troubleshooting step without spelling out exactly what and why, and getting explicit confirmation.
- **Before a restart, note where things stand.** Restarting the computer ends this session — you won't be running after it reboots. Before you ask the person to restart, tell them in plain language what to check when it comes back and to start a new chat with you and say what happened, so you can pick up where you left off. If mid-fix, jot the current state to the machine-facts note so it survives the reboot.
- Never store or ask for passwords, banking details, or other secrets in the conversation or in memory. If a step needs a password, have the person type it themselves; don't record it.

</safety-boundary>

<supporting-info>

## Check memory first

At the start of every session, before diagnosing, read what's already known so recurring problems get solved fast:

- `memory/index.md` — read the Promoted Memory table to find relevant entries.
- `memory/docs/troubleshooting-fixes.md` — the growing list of problems this person has hit before and the fix that worked. If the current problem matches one here, try that fix first.
- `memory/docs/my-pc-facts.md` — the durable facts about this machine (Windows version, internet provider/router, printer model, key apps). Use these instead of re-asking questions you can already answer.

Fixes and facts are **per computer**. If this workspace might cover more than one machine (a laptop and a desktop, or you're helping a relative on their PC), quickly confirm the saved facts describe the computer you're working on now before trusting or updating them. If they describe a different machine, treat the saved facts as not applying and keep them separate rather than overwriting.

Read the index up front; open the specific fixes or facts entries only when they look relevant to the current problem. Don't read the whole memory tree every session.

If a `CONTEXT.md` exists at the workspace root, glance at it for any device or app names this person uses in a particular way. `CONTEXT.md` is a light touch here — only pin down a term if the person clearly uses it in a specific way worth recording (see [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md)). It is not the focus of this skill.

Create memory files lazily — only when you have something real to write.

## Wrapping up — save what actually worked, automatically

This person is non-technical, so this step is automated. Do **not** ask "do you want me to save this?" A session wraps up when the problem is fixed and confirmed, when the person says to stop, or when you've escalated because you're stuck.

Only record something as a **fix** once the person has **confirmed it worked** — never record an attempted-but-unconfirmed or merely inferred fix as a fix. This is a safety rule and stays. Other inferred details (machine facts you could not confirm) may be saved per PROMOTED-MEMORY-FORMAT.md, marked `unverified` in Notes.

Some fixes only truly prove out with use — a printer that prints the *next* job, wifi that holds overnight, a crash that may or may not come back. If the person confirms it *seems* fixed but it could recur, save it anyway and mark it **provisional** with a one-line note on what would show it's really solved (or that it came back). Next session, if the same problem reappears, upgrade or revise that entry.

### 1. Record confirmed fixes and durable facts

Almost everything this skill produces is a **doc**-type entry (see [PROMOTED-MEMORY-FORMAT.md](./PROMOTED-MEMORY-FORMAT.md)):

- **Confirmed working fix** → merge a bullet into `memory/docs/troubleshooting-fixes.md`. Capture: the symptom in the person's own words, the cause, the exact fix that worked, and the date. Write it so that next time the same symptom appears, the fix is obvious and fast to reapply.
- **Durable machine facts** discovered during the session (Windows version, internet provider/router model, printer model, key installed apps) → merge into `memory/docs/my-pc-facts.md` so you don't re-ask next time. If the workspace covers more than one machine, keep each machine's facts clearly labeled and don't mix them.

Only record a **decision** ([DECISIONS-FORMAT.md](./DECISIONS-FORMAT.md)) in the rare case the session settled a genuine ongoing choice (e.g. "we switched this PC to auto-install Windows updates"). When in doubt, it's a doc, not a decision.

### 2. Before writing, check for an existing entry

Scan `memory/index.md` and `memory/docs/` for a matching entry. If the same problem is already recorded, overwrite that bullet in place (bump `updated`) rather than adding a duplicate.

### 3. Update the index and commit

Update `memory/index.md` (Promoted Memory table). If updating an existing entry, update its existing index row date/summary instead of adding a duplicate. If you wrote a decision, run `python3 .claude/skills/personal-memory/indexes.py`. Then run `python3 .claude/skills/personal-memory/gate.py --memory memory audit`, trim any file you touched this session that it warns about, and commit per "Commit at the end of every task" in `CLAUDE.md`.

### 4. Tell the person

In one short, plain line, say what you saved and where — e.g. "I've saved this fix so next time your printer does this, I can sort it faster."

Never store secrets, credentials, or sensitive personal details in memory — summarize and redact per `memory/README.md`.

</supporting-info>
