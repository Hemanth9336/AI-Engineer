---
type: lesson
title: "Worktree sources and settings"
minutes: 10
---

## Which commit a worktree starts from

By default, new worktrees branch from the repository's **default branch**, not from whatever you have checked out. To branch from your current HEAD instead:

```json
{ "worktree": { "baseRef": "head" } }
```

`baseRef` cannot name a branch; to start from a specific branch, create the worktree with `git worktree add` and run `claude` inside it.

## From a pull request

```bash
claude --worktree "#1234"
claude --worktree https://github.com/acme/app/pull/1234
```

Claude Code fetches that change and starts the worktree on it - the fastest way to review or fix a PR without touching your own branch.

## Copying gitignored files: .worktreeinclude

A worktree has no `.env`. List what to copy in `.worktreeinclude` at the project root (gitignore syntax):

```text
.env
.env.local
config/secrets.json
```

Only files that match **and** are gitignored are copied, so tracked files are never duplicated. Think before listing secrets: every agent worktree gets a copy.

## What worktrees share with the main checkout

- The `.git` directory - commits made in a worktree are visible everywhere at once.
- Project-scope plugins.
- "Yes, and don't ask again" approvals, saved to the main checkout's `.claude/settings.local.json`.
- Untracked skills, agents, and commands from the main checkout when the worktree has none.

## Cleanup

Worktrees Claude creates for subagents and background sessions are swept after `cleanupPeriodDays`. Worktrees you made with `git worktree add`, and `--worktree` sessions you did not background, stay until you remove them.

## Commands this node introduces

The `worktree.baseRef` setting, `.worktreeinclude`, and `claude --worktree "#<pr>"`.
