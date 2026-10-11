---
name: handoff
description: Create a handoff document for another agent or session in this workspace to continue current work. Use when user asks for handoff, session handoff, continuation prompt, or next-session context.
---


# Handoff

Preserve current session context so a fresh session or agent in this workspace can continue work without rereading the whole conversation.

## Workflow

1. Identify next-session focus from user arguments, if provided.
2. Gather only necessary context from current session:
   - goal and current state
   - decisions made
   - files, artifacts, tickets, URLs, commands, and tool results that matter
   - blockers, risks, assumptions, and next steps
   - suggested skills for next session
3. Avoid duplicating content already captured in artifacts, PRDs, plans, ADRs, issues, commits, or diffs. Reference those by path, ticket ID, URL, or commit instead.
4. Create the handoff document under a hidden workspace-local `.handoff/` folder, creating the folder first if needed. Do not use OS temp folders such as `/var/folders`, `/tmp`, or `%TEMP%`. Do not use `mktemp`, because it may append random text after `.md`; the final filename must end exactly in `.md`.

   macOS/Linux shell:

   ```bash
   mkdir -p .handoff
   HANDOFF_PATH=".handoff/handoff-$(date +%Y%m%d-%H%M%S)-$RANDOM.md"
   : > "$HANDOFF_PATH"
   ```

   Windows PowerShell:

   ```powershell
   $Folder = Join-Path (Get-Location) ".handoff"
   New-Item -ItemType Directory -Force -Path $Folder | Out-Null
   $Path = Join-Path $Folder "handoff-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
   New-Item -ItemType File -Force -Path $Path | Select-Object -ExpandProperty FullName
   ```

   Read the newly created file before writing to it. Handoff files are local workspace artifacts and must remain gitignored. Valid handoff paths look like `.handoff/handoff-20260616-143022-12345.md`; invalid paths look like `.handoff/handoff-XXXXXX.md.dS3GV3BRyU` because they do not end exactly in `.md`.
5. Write concise Markdown handoff. Use normal prose in document, not chat-style caveman prose.
6. Return only short copy-paste prompt for next session. Prompt must reference the workspace-relative handoff file path and name any suggested skills to start with. Do not inline or reprint document contents.

## Handoff document shape

```markdown
# Handoff: <short topic>

## Next-session focus

<what next session should accomplish>

## Current state

<where work stands now>

## Key context

- <decision, evidence, or fact>
- <path, URL, ticket ID, command, or artifact reference>

## Suggested skills

- `<skill-name>` — <why>

## Next steps

1. <first action>
2. <second action>

## Risks / blockers

- <if any>
```

## Output prompt shape

```text
Continue from handoff: .handoff/<handoff-file-name>. Focus on <next-session focus>. Start with skill(s): <skill names>, if useful.
```
