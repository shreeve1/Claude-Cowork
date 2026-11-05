# Project skills

A project skill packs one project's repeatable steps into a Cowork skill. Create one only with the owner's approval for that project; each project needs its own approval.

## When to recommend

Recommend a skill when the project's instructions or notes describe repeatable steps (a process run again and again, such as a monthly report), not reference (facts, background, files). Reference stays in the project folder. Done when the owner has heard the recommendation with one example step and answered yes or no for this project.

## What the skill holds

Steps and decisions about how to do the work. It keeps no facts. Facts, files and instructions live in `<home>/<short>/README.md`, so they change in the folder and need no reinstall. The skill opens the project first, through SKILL.md "Open a project".

## Steps

1. **Name.** Use the project short name. Check it against the installed skills listed in this session and the shipped skill names, which are the keys of `.claude/cowork/skills/index.json`. If that index is absent, ask the owner whether a ready-made card uses the name. On a clash, ask the owner for another name. Done when no skill has the name.
2. **Write the source** at `<home>/<short>/skill/SKILL.md` from the template below. Replace every `<...>` placeholder. The description says what the skill does and when to use it. Each step ends with how to tell it is done. Cowork's built-in skill-creator, if installed, may draft it; the same rules apply. Done when no placeholder is left.
3. **Check** the frontmatter against Cowork's upload rules: keys only `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`; description at most 1024 characters, no `<` or `>`, no unquoted `: ` (quote the value); name kebab-case, at most 64 characters, equal to the folder name. Done when each rule holds.
4. **Package** with Bash (python3 runs in the sandbox) into the session's outputs folder (the folder `present_files` presents from, outside the workspace). Replace `<session outputs>` with that folder's sandbox path. The `.skill` zip holds exactly `<name>/SKILL.md`, the same layout as the shipped cards. Done when the zip lists only that file.

   ```python
   import os, zipfile
   name, src, out = "<name>", "<home>/<short>/skill/SKILL.md", "<session outputs>"
   os.makedirs(out, exist_ok=True)
   with zipfile.ZipFile(f"{out}/{name}.skill", "w", zipfile.ZIP_DEFLATED) as z:
       z.write(src, f"{name}/SKILL.md")
       print(z.namelist())
   ```

5. **Present** the `.skill` with `present_files` and say: "Click **Save skill** on this card, then tell me when you have finished." Done when the owner confirms.
6. **Verify** the skill is available in this session. Then add `Skill: <name>` to the project README (SKILL.md "Find the home") and commit per workspace rules. Done when the skill is listed and the README line exists.

A card without **Save skill** means the organisation forbids skills. Report the installation blocked and stop there: the owner's admin decides. The README stays unchanged, the source stays in the folder, and the project keeps working through the opener.

## Update

Edit `<home>/<short>/skill/SKILL.md`, repackage (step 4), present it, and the owner clicks **Save skill** again. Fact changes go in the project folder only. Done when the owner confirms the new save.

## Template

```markdown
---
name: <skill-name>
description: <description>
---

# <skill-name>

Open the project first: run the `project-import` skill's Open a project branch for `<short>`, then read `<home>/<short>/README.md` for facts, files and instructions.

## Steps

1. **<Step name>.** <What to do and decide.> Done when <check>.
```
