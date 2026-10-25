---
type: lesson
title: "Adding a root is a permission decision"
minutes: 12
---

Adding a directory feels like convenience, but it is the same kind of decision as an allow rule: you are telling Claude Code that everything under that path is in scope.

## Before you add a root, ask

- **Is the whole tree safe to read?** A root at `~` exposes `~/.ssh`, `~/.aws`, and every other project. Add the narrowest folder that contains what you need: `../shared/contracts`, not `..`.
- **Should the agent edit it?** Added roots follow the permission mode. In `acceptEdits`, the agent may now change the shared folder too.
- **Who else depends on it?** A shared contracts folder edited by an agent working on one app can break every other consumer.

## Prove the boundary

Do not assume the grant did what you meant. Run the same read twice:

1. Without `--add-dir`: the read outside the working folder is refused, and the envelope's `permission_denials` lists it.
2. With `--add-dir`: the read succeeds and the answer contains the real value.

Keeping both envelopes is evidence that the boundary exists and that the grant - and only the grant - opened it.

## Added root or worktree?

| Situation | Use |
|---|---|
| Read (or lightly edit) a different folder alongside your project | `--add-dir` |
| A second, isolated copy of **the same repo** on another branch, so two tasks don't trample each other | a git worktree (`claude -w <name>`, topic 026) |
| Two unrelated repos that must change together | one session per repo, or add the second as a root and review both diffs |

A worktree is for parallel work on one repository; an added root is for reaching another one.

## Commands this node introduces

`jq .permission_denials before.json` proves the boundary held before the grant.
