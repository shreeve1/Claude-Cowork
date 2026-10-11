#!/bin/sh
# Auto-commit: commits every change in the workspace when the agent finishes a turn.
# Wired as a Claude Code Stop hook in .claude/settings.json (see INSTALL.md step 10).
# Never pushes. Never skips the git hooks: if a hook rejects the commit (for example a
# secret-scan hit), the work stays uncommitted and the reason is printed.

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}" 2>/dev/null || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
[ -n "$(git status --porcelain 2>/dev/null)" ] || exit 0

git add -A >/dev/null 2>&1
if ! out=$(git commit -q -m "auto: $(date '+%Y-%m-%d %H:%M')" 2>&1); then
    echo "autocommit: commit not made; changes left uncommitted." >&2
    printf '%s\n' "$out" >&2
fi
exit 0
