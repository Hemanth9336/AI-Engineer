---
type: lesson
title: "What the VS Code extension adds over the terminal"
minutes: 14
---

The VS Code extension puts Claude Code in a graphical panel. It ships its own copy of the CLI, and shares conversation history with the terminal, so `claude --resume` continues an extension conversation. (Installing it doesn't add `claude` to your PATH.) It needs VS Code 1.94 or later, and works in Cursor and other VS Code forks.

| You get | How |
|---|---|
| **Native diffs** | In Manual mode each edit opens side by side. Accept, reject, or edit the proposal before accepting. Per-change Accept and Reject buttons appear for diffs of up to 100 changes |
| **Plan review** | In plan mode the plan opens as a Markdown document you can comment on inline. `/plan open` reopens it |
| **Precise @-mentions** | `@file`, `@folder/`, and `Option+K` / `Alt+K` to insert the selection as `@app.ts#5-10`. `@terminal:name` for terminal output |
| **Selection awareness** | Claude sees your selected text automatically, unless the file is excluded or gitignored |
| **Checkpoints** | Hover a message: fork the conversation, rewind code, or both |
| **Tabs and windows** | Several conversations side by side |

The CLI still has things the panel doesn't, such as the `!` bash shortcut, tab completion and the full set of commands. Running `claude` in VS Code's **integrated terminal** gives you the CLI *and* the IDE integration (diffs, diagnostics) automatically. From an external terminal, run `/ide` to connect.

## Commands this node introduces

The VS Code panel, native diffs, plan review, `Option+K`/`Alt+K` selection mentions, `@terminal:`, checkpoints, `/ide`, and `claude --resume` across surfaces.
