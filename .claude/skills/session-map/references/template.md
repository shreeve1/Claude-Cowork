# Session map template

## Template

```markdown
---
status: active
created: 2026-11-13
---
# <Title>

## Destination
<What is true at the end and how the owner will check it.>

## Stages
| # | Stage | Depends on | Status | Evidence |
| --- | --- | --- | --- | --- |
| 1 | <Outcome> | - | Todo | - |

## Next
### Stage 1: <Outcome>
- **Goal:** <Result>
- **Done when:** <Observable check>
- **Starts from:** <Inputs>
- **Approaches:** <Options, pick and reason.>

## Open questions
- None

## Decisions
- None

## Constraints
- <Rule every stage carries>

## Found along the way
- None

## Log
- 2026-11-13 Map started.
```

## Fields

Keep maps at `docs/maps/<slug>.md`; use two to four lowercase hyphenated words. Frontmatter has `status` (`active`, `paused`, `done`, `dropped`) and `created` (`YYYY-MM-DD`), followed by one level-one title.

Destination takes one to three lines and states the end condition and how the owner checks it. Stages uses exactly the table header above. IDs match `1`, `2`, or `2a`; they stay stable, and a split makes lettered children. Stage names state outcomes. Dependencies are `-` or comma-separated IDs.

Status begins with Todo, Active, Waiting, Done or Dropped; punctuation after the word is fine (`Dropped: reason`). Waiting names who or what holds the gate in its Status note; its Open question, if any, names the blocked stage. Clear both when the gate resolves. A Dropped reason goes in its Status note or Evidence. `map.py claim` sets Active. Done rows need evidence: backticked commits, repo-relative paths, URLs, or other-repo evidence written as `repo@sha` for commits and `repo:path` for paths.

Each frontier brief has **Goal**, **Done when**, and **Starts from**. An Active brief also has **Where it stopped**, naming completed work, remaining work and branch or worktree. **Approaches** and **Leaves for later** are optional. Approaches is one line: options considered, the pick and why. Use `None` when there are no briefs. Open questions name what they block. Attribute decisions as `(<owner name>, YYYY-MM-DD)` or `(agent's call, YYYY-MM-DD: reason)`.

Constraints carry rules shared by every stage. Found along the way carries facts later stages need. Log has one dated bullet per session, oldest first. At finish, add Outcome after Destination. Keep the map at 250 lines or fewer; move detail to linked files.
