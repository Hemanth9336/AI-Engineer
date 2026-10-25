---
type: lesson
title: "Vim mode and prompt editing"
minutes: 10
---

If your fingers think in vim, the prompt can too.

```json
{
  "editorMode": "vim",
  "vimInsertModeRemaps": { "jj": "<Esc>" }
}
```

Put this in `~/.claude/settings.json` (or toggle **Editor mode** in `/config`). `vimInsertModeRemaps` maps a two-key sequence typed in INSERT mode to Escape; it is user-scoped on purpose - a repository cannot remap your keystrokes.

## What you get

| Mode | Keys |
|---|---|
| NORMAL | `h j k l`, `w b e`, `0 $`, `gg G`, `x`, `dd`, `dw`, `cw`, `ciw`, `p`, `u`, `.` |
| INSERT | `i a I A o O` to enter, `Esc` (or your remap) to leave |
| VISUAL | `v` / `V` to select, then `d`, `y`, `c` |

At the first or last line, `j` / `k` move through **prompt history** instead of the cursor. `Enter` still sends the prompt from either mode.

## When a prompt gets long

Vim mode is for quick edits. For a long, structured prompt, press `Ctrl+G`: your real `$EDITOR` opens with the prompt, and saving and closing puts the text back. Pair it with a prompt file (topic 013) when you will reuse it.

## The status line knows your mode

When vim mode is on, the JSON Claude Code sends to your status line script includes `vim.mode` (`NORMAL`, `INSERT`, `VISUAL`, `VISUAL LINE`), so the status line can show it.

## Commands this node introduces

The `editorMode` and `vimInsertModeRemaps` settings, and `/config` to toggle them.
