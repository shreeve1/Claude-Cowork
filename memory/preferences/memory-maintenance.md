---
title: Memory Updates - Replace Before Appending
summary: When updating memory, search for the existing note first and replace or merge in place; append only when nothing covers the fact.
type: preference
status: promoted
created: 2026-10-18
updated: 2026-10-18
topics: [preference, memory, maintenance]
---

## Active memory

When updating memory for a fact, route or preference that might already be recorded:

1. **Search first.** Search `memory/` for the topic's keywords before writing anything. Do not write from a blank slate assuming the fact is new.
2. **Replace or merge in place.** If a file already covers it, overwrite the stale claim so the file states only what is true now: one authoritative statement per fact, not a version history inside the file (git keeps history).
3. **Append only when genuinely new.** A new bullet or new file is right only when no existing note covers the fact.
4. **Sweep references.** After replacing a claim, search for other files that repeat or link the old wording and update those too, including summaries and dates in `memory/index.md`.

The measure of success: a future session reading only the touched files finds one consistent truth, not a corrected claim next to its superseded version.

## Notes

- Last reviewed: 2026-10-18
- Captured 2026-10-18 after one note was rewritten three times in a day before it was cleaned up; replace-first became the standing rule.
