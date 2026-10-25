---
type: lesson
title: "Changing code safely with the agent"
minutes: 14
---

An agent can change many files quickly. Safety means you can always see, review, and undo what it did.

## A safety net before the first edit

- **A branch:** `git switch -c fix/level-count`. `main` stays untouched until review.
- **A clean tree:** `git status` shows nothing before you start, so every later change is the agent's.
- **Checkpoints:** in an interactive session, `/rewind` (or `Esc Esc`) rolls the code and the conversation back to before a prompt. A commit is a checkpoint that survives the session.
- **Isolation for bigger work:** `claude --worktree fix-levels` runs in its own git worktree, so your checkout is never touched.

## Commit the steps separately

1. `test: reproduce level miscount` - only the failing regression test (and your bug notes).
2. `fix: count the level field only` - only the code change.

A reviewer can check out commit 1 and watch the test fail, then commit 2 and watch it pass. That is proof, not a claim.

## Don't let the fix edit the tests

The quickest way to make a failing test pass is to change the test. For the fix run, take that option away:

```bash
claude -p "Fix logcount.py so the tests pass. Do not modify tests." \
  --allowedTools Read Edit "Bash(python3 -m unittest *)" \
  --disallowedTools "Edit(tests/**)"
```

`Edit(...)` rules cover Write as well, and a disallowed rule wins over an allowed one.

## Review the diff, not the summary

`git diff main...HEAD` shows exactly what changed. Read it before merging, whatever the agent's final message says.

## Commands this node introduces

`git switch -c`, `/rewind`, `claude --worktree`, `--disallowedTools "Edit(tests/**)"`, and two-commit fixes.
