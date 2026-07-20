# Update

Copy and paste this into your AI agent:

> Clone the latest `https://github.com/shreeve1/Claude-Cowork` into a local temp dir (cloning into the mounted workspace fails). Update from the committed `.skill` bundles in the clone's `.claude/cowork/` folder, plus the `CLAUDE.md` at the repo root. Ignore `.DS_Store`.
>
> **Skills.** For each `.claude/cowork/<name>.skill` in the clone, compare it byte-for-byte against my workspace copy at `.claude/cowork/<name>.skill`. Output only the bundles that are new or changed as downloadable `.skill` files in chat, so the desktop app shows a "Save skill" button for each — I click Save to re-register them. Skip unchanged bundles silently. If I have no `.claude/cowork/` baseline, or a comparison fails, output all of them. After presenting, copy the presented `.skill` files into my `.claude/cowork/` so the next update can diff against them.
>
> **CLAUDE.md.** Compare the clone's root `CLAUDE.md` against my workspace root `CLAUDE.md`. If I don't have one, write it. If mine differs, show me what would change and propose the update — apply it only after I approve. If they're identical, skip.
>
> Finish by listing which skills you updated, which you skipped as unchanged, and what you did with CLAUDE.md. If nothing changed, say so and output nothing.
