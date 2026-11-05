---
name: project-import
description: Project work - open a project so the conversation is aligned with its goal, instructions, tasks and memory; import Claude app Projects into this workspace; or turn a project's repeatable steps into its own skill.
---

# Project

Keep each project in one folder in the owner's workspace. Three branches: open a project, import a Claude Project, create a project skill. Ask the owner in plain text.

`personal-memory` supplies the README format and memory notes. Find it in the owner's installed Cowork skills, never at a fixed path or in the maintainer source tree, and check that `SKILL.md` and `supporting-templates.md` are readable. If it is absent, ask the owner to attach the workspace ZIP, then present its ready-made `personal-memory.skill` with `present_files` for **Save skill**. Verify access after saving.

## Find the home

Read `memory/schema.json` (`client_folder`, `client_dirs`) and `memory/preferences/document-scaffolding.md`. The folder map says where a project lives. `<home>` is the folder that holds the project folder, one of: `projects/` (an independent project); `<client_folder>/` (the project is itself a tracked thing); `<client_folder>/<client>/projects/` (a project that belongs to one tracked thing, using the existing projects document folder). The project folder is always `<home>/<short>/`. Say the owner's word for the tracked thing, whatever the schema calls it. When several homes fit, recommend one per project and let the owner choose.

```text
<home>/<short>/
  README.md        # Project README from personal-memory/supporting-templates.md
  instructions.md  # approved working instructions, if any
  files/           # imported knowledge files
  skill/           # project skill source, if any
```

Two plain lines go inside the README's Files section:

```text
Source: Claude Project <id>, imported YYYY-MM-DD
Skill: <name>
```

`Source:` marks an import, so a re-import is detected. `Skill:` appears only once the project has a skill. A glossary row maps the project's display name to `<short>`.

## Open a project

1. **Find.** Match the owner's words against glossary rows and the titles of READMEs under `projects/`, `<client_folder>/` and `<client_folder>/*/projects/`. One match: use it. If several match, ask which. None: list the projects and offer Import or starting a new one. On the owner's yes to a new one, create `<home>/<short>/README.md` from personal-memory's Project README template, then open it.
2. **Load.** Read `README.md`, `instructions.md`, every memory note and task record the README links, and the `tasks/index.md` rows for this project: rows whose task this README links, or whose task record sits inside this project's folder. Another project's task row is not this project's. Done when every link is opened or reported missing.
3. **Brief**, about 150 words: goal, instructions in force, open tasks and next steps, key facts, gaps or conflicts. When the README has a `Skill:` line, name the skill in the briefing. End by asking what we are doing today.
4. **Hold.** Follow `instructions.md` for the conversation; workspace and safety rules win, and you name any conflict once. Switching projects drops the old instructions and says so.

## Import

To bring Claude app Projects into this workspace, read [import.md](import.md) first.

## Project skills

To turn a project's repeatable steps into its own skill, read [project-skills.md](project-skills.md) first. Each skill needs the owner's approval for that project.
