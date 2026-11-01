# Project, pending proposal and research templates

Copy only the needed format. These examples are not live records. Task lifecycle and cleanup are in [task operations](tasks.md).

## Project README

Use for a real goal spanning related tasks or files. In a workspace, save to `projects/<short>/README.md`; a client-owned project can stay under its existing client project path. In a code repository, use its existing README or link to it instead of creating a duplicate. Read the entry point before work on that project.

Create only the subfolders the agreed folder map needs. Replace placeholders with grounded information or Unknown; remove unused sections. A README groups work, not permissions. Reference saved task records by stable ID and path without copying their live status or next steps. No task is created or picked up merely by linking it. Lasting facts and verified agent procedures stay in memory; human runbooks may live with project files.

```markdown
# <Project name>

## Goal

<The outcome and why it matters.>

## Scope

<What is included and what is not.>

## Completion check

<Observable evidence that the goal has been reached, or Unknown.>

## Tasks

- <Stable task ID and current workspace-relative path; or None yet.>

## Files

- <Existing workspace-relative file/folder and what it contains; or None yet.>

## Memory and procedures

- <Existing authoritative memory, decision, hub or verified procedure path; or None yet.>
```

Do not invent dates, a project status system or a second task index. Keep references current when relevant records move or archive. When there are no durable notes, the README is the entry point; no generated hub is required.

## Pending proposal

Use when a task produces a proposed procedure, rule or other standing change that still needs approval or verification. Save it separately before archiving the originating task, using `notes/<topic>-proposal-YYYY-MM-DD.md` unless the owner or an applicable skill specifies another home. Never overwrite an existing record.

A proposal preserves a decision to consider; it is not an approved instruction. Completing its source task does not approve the proposal or authorize its execution. A separate active task is created only with the owner's agreement.

Replace placeholders with grounded information, or state Unknown. Use workspace-relative paths and a stable task ID so the source remains findable after archival. Never invent approval or verification dates. Remove placeholder bullets that do not apply.

```markdown
# Proposal: <short title>

Status: proposed; not approved for use.
Created: <YYYY-MM-DD>
Updated: <YYYY-MM-DD>

## Proposed change

<What would change, and where it would belong if approved.>

## Reason

<The problem this addresses and why the change is worth considering.>

## Evidence

- Source task: <stable task ID and current or archived workspace-relative path>.
- <Observed finding and its source; distinguish assumptions from observations.>

## Verification so far

<What was actually tested, its result and evidence. Say Not tested when applicable.>

## Still needed

- <Approval or decision needed, who can provide it, and what they must decide.>
- <Verification still required before promotion or use.>
```

Keep Still needed current as evidence or owner decisions arrive. Preserve explicit approval evidence if given, without inventing it or treating document edits as approval. Promote only through the applicable memory or procedure workflow. Until any required verification and approval are satisfied, the proposal remains outside authoritative memory. Pending approval never blocks archival of its source task.

## General research record

Use for research that has no skill-specific format. Use the agreed folder map: research confined to one project uses its configured research folder; otherwise default to `research/<topic>-YYYY-MM-DD.md`. An owner-named or skill-required path takes precedence. An applicable skill's own section order takes precedence.

Use plain words, answer first, and distinguish evidence from guesses. Apply `memory/preferences/research-documents.md` and `memory/preferences/writing.md` when those local preferences exist. Every Findings block starts with a one-line answer and has at most seven sourced bullets, one fact per bullet. State uncertainty and checks not performed. When research continues, append a dated Findings block rather than rewriting earlier findings; explicitly identify any earlier conclusion that new evidence corrects. Replace Path to Close and Questions with the current remaining work.

```markdown
# Research: <question or topic>

## Question and scope

<The question to answer, boundaries and any relevant source-task ID.>

## Findings: <YYYY-MM-DD>

<Answer in one line, or say what is not yet established.>

- <One observed fact or clearly labelled uncertainty. Source: record, file or URL.>

## Path to Close

- <Owner> — <one next action and the observable result that finishes it>.

## Questions

- <One sentence asking for the decision or missing information and why it matters?>
```

Use None under Path to Close or Questions when nothing remains. Add only real sources, using workspace-relative file paths, system record references or plain URLs. References to existing policy identify the policy's home rather than copying it into research. Keep raw correspondence, credentials and full tool logs out of the record. Research findings do not authorize sending messages or changing systems.
