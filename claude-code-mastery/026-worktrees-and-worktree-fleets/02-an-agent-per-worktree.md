---
type: lesson
title: "An agent per worktree"
minutes: 10
---

Claude Code creates and enters worktrees for you:

```bash
claude -w fix-tax                       # interactive, in .claude/worktrees/fix-tax on branch worktree-fix-tax
claude -p -w add-docs "Add docstrings to report.py and commit"   # headless, same idea
```

- `--worktree <name>` (or `-w`) creates `.claude/worktrees/<name>/` at the repository root on a new branch `worktree-<name>`, branched from the default branch.
- Omit the name and Claude generates one.
- Interactive `-w` needs the folder trusted; `-p -w` skips the trust check.
- Add `.claude/worktrees/` to `.gitignore` so worktrees do not show up as untracked files in the main checkout.

## Isolation is enforced

While a session is in a worktree, Claude Code **blocks** file edits that target the main checkout, commands whose working directory is the main checkout, and git commands redirected into it (`git -C`, `GIT_DIR`, `cd` then git). Subagents spawned from that session inherit the same rules. Commands like `cp` or a shell redirect are not tracked, so isolation is a guardrail, not a sandbox.

## Leaving and coming back

When an interactive worktree session exits with work in it, Claude asks whether to keep or remove the worktree, and prints the `claude --worktree <name> --resume` command to return. A worktree with no changes is removed automatically.

Subagents can get their own worktree too: `isolation: worktree` in the agent's frontmatter.

## Commands this node introduces

`claude -w <name>` / `claude --worktree <name>`, and `claude --worktree <name> --resume`.
