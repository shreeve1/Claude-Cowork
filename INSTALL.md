# Install

Copy and paste this into your AI agent:

> **Use your shell (bash) for this — do not fetch files one by one over the web.** Run a shallow clone into a temp dir (cloning into the mounted workspace fails):
>
>     git clone --depth 1 https://github.com/shreeve1/Claude-Cowork /tmp/cowork-install
>
> If the clone fails (e.g. the sandbox can't reach GitHub), stop and tell me plainly — do not fall back to fetching individual files over the web, and do not try to reconstruct the `.skill` bundles by hand (they're binary and won't survive it).
>
> Everything I need is committed in the clone: the pre-built `.skill` bundles in `.claude/cowork/`, plus the `CLAUDE.md` at the repo root. The bundles are: `cowork-onboarding.skill`, `personal-memory.skill`, `professional-guidance.skill`, `prototype.skill`, `talk-it-through.skill`, `workflow-builder.skill`. List `/tmp/cowork-install/.claude/cowork/*.skill` to confirm the set; ignore `.DS_Store`.
>
> **Skills.** For each `.skill` bundle in the clone, compare it byte-for-byte against my workspace copy at `.claude/cowork/<name>.skill`. Output only the bundles that are new or changed as downloadable `.skill` files in chat, so the desktop app shows a "Save skill" button for each — I click Save to register them. Skip unchanged bundles silently. If I have no `.claude/cowork/` baseline, or a comparison fails, output all of them. Then, best-effort, copy the presented bundles into my `.claude/cowork/` **using the shell** (`cp` — the file Write tool is blocked under `.claude/`) so future updates can diff against them; if that copy fails, don't stall — the Save cards are the real deliverable.
>
> **CLAUDE.md.** Compare the clone's root `CLAUDE.md` against my workspace root `CLAUDE.md`. If I don't have one, write it. If mine differs, show me what would change and propose the update — apply it only after I approve. If they're identical, skip.
>
> Finish by listing which skills you presented, which you skipped as unchanged, and what you did with CLAUDE.md.
