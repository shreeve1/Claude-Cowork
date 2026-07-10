# Update

Copy and paste this into your AI agent:

> Pull the latest from `https://github.com/shreeve1/Claude-Cowork` (clone to a local temp dir — cloning into the mounted workspace fails). Compare its `.claude/skills/` and `agents-library/` against my workspace: add missing files, update changed ones, but keep files that exist only in my workspace (don't delete), and ignore `.DS_Store`. Track which skills you add or change.
>
> Then, only for the skills whose `cowork/SKILL.md` you just added or updated (skip any already identical in my workspace), package each as an installable `.skill` bundle — a zip with `SKILL.md` at the root and a lowercase `.skill` extension — so the desktop app shows a "Save skill" button. Before zipping, in each loader's `description` frontmatter replace any angle-bracket placeholders (e.g. `<name>`, `<slug>`) with curly braces (`{name}`, `{slug}`); the app rejects descriptions with XML-like tags. If nothing changed, say so and output nothing.
