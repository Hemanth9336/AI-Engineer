---
type: lesson
title: "Panes, visual review, and parallel sessions with automatic worktrees"
minutes: 14
---

## Panes

The Code tab arranges **panes**: chat, diff, browser, terminal, file, plan, tasks, subagent, and on macOS the iOS Simulator. Drag them around, pop one into its own window, or close the focused one with `Cmd+\` / `Ctrl+\`.

| Pane | Use |
|---|---|
| **Diff** | Click the `+12 -1` counts on the Changes card. Comment on lines, then submit all comments with `Cmd+Enter`. Claude addresses them as a batch |
| **Code review** | `/code-review` in the prompt box gives a Code review card. **Walk through in diff** steps through findings, and **Apply fixes** applies them |
| **Browser** | `Cmd+Shift+B`. A dev-server preview that Claude can verify after each edit, in a **clean profile** with none of your logins |
| **Terminal** | ``Ctrl+` ``, in the same environment Claude uses |
| **File** | Edit files directly in local sessions. It's view-only for cloud, SSH and WSL sessions |
| **Side chat** | `Cmd+;` or `/btw`, for a quick question that stays out of the main thread (not saved to disk) |

## Parallel sessions and automatic worktrees

Start more sessions with **+ New** (`Cmd+N`), and cycle through them with `Ctrl+Tab`. Two sessions editing one checkout will trip over each other, so turn on the **Worktree** toggle on the project folder control:

- Each session gets its own **git worktree** under `<project-root>/.claude/worktrees/` by default, on its own branch. The location and branch prefix are configurable in Settings.
- Gitignored files the session needs, such as `.env.example` or local config, can be copied in by listing them in `.worktreeinclude`.
- Isolation requires git. Commit worktree changes before archiving a session. Worktrees are cleaned up about 30 days after a session is archived.
- The CLI equivalent is `claude --worktree <name>` (`-w`).

## Commands this node introduces

Panes, the diff pane with batched comments, the Code review card, the browser pane, side chat (`/btw`), the **Worktree** toggle, `.claude/worktrees/`, `.worktreeinclude`, and `claude --worktree`.
