---
type: lesson
title: "Git as the durable checkpoint"
minutes: 12
---

`/rewind` is a convenience inside one session. **Git is the checkpoint that always works**: it sees every change, whatever made it, and it outlives the session.

## The workflow

```bash
git status --short                 # 1. start clean (commit or stash first)
git tag cp-before-cleanup          # 2. mark the point you may return to
claude -p "..." --permission-mode acceptEdits   # 3. let the agent work
git status --short                 # 4. see EVERYTHING it changed - including Bash deletions
git diff                           #    and review the content
```

Then decide:

| Outcome | Command |
|---|---|
| Keep it all | `git add -A && git commit -m "..."` |
| Undo it all | `git reset --hard cp-before-cleanup && git clean -fd` |
| Undo one file | `git restore --source=cp-before-cleanup -- path/to/file` |
| Undo deleted files only | `git restore --source=cp-before-cleanup -- legacy/` |
| Keep some hunks | `git add -p`, commit, then reset the rest |

`git reset --hard` discards tracked changes; `git clean -fd` removes untracked files and folders the agent created (add `-n` first to preview). Both are destructive by design - that is the point of having tagged the checkpoint first.

## Rules that make this safe

- **Start from a clean tree**, so "what the agent changed" equals "what git shows".
- **Tag (or commit) before every risky run.** Tags are free.
- **Look at `git status`, not just `git diff`.** Deleted and new files do not show in a plain `git diff`.
- **Never let a run you have not reviewed `git push`.** Add `Bash(git push *)` to `ask` or `deny`.

## Commands this node introduces

`git tag <name>`, `git status --short`, `git reset --hard <tag>`, `git clean -fd`, and `git restore --source=<tag> -- <path>`.
