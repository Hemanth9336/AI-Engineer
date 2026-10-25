---
type: lesson
title: "The status line"
minutes: 10
---

The **status line** is a row under the prompt that shows whatever **your script** prints. Claude Code pipes a JSON description of the session to the script's stdin after each assistant message and displays the script's stdout.

```json
{
  "statusLine": { "type": "command", "command": "~/.claude/statusline.sh", "padding": 0 }
}
```

`/statusline show model, context percentage, and cost` asks Claude to write the script and the setting for you.

## What arrives on stdin (excerpt)

```json
{
  "model": { "id": "claude-opus-5-5", "display_name": "Opus 5.5" },
  "workspace": { "current_dir": "/root/mastery/021-terminal", "project_dir": "/root/mastery/021-terminal" },
  "cost": { "total_cost_usd": 0.1342, "total_duration_ms": 48211 },
  "context_window": { "used_percentage": 42.5, "context_window_size": 200000 },
  "vim": { "mode": "NORMAL" },
  "session_id": "...", "version": "2.1.310"
}
```

Other fields include `effort.level`, `session_name`, `worktree.*`, `pr.*`, and rate-limit percentages. Some are **absent** at times - `context_window.used_percentage` is null before the first reply, `vim` only exists in vim mode - so the script must cope.

## A robust script

```bash
#!/bin/bash
in=$(cat)
model=$(jq -r '.model.display_name // "?"' <<<"$in")
pct=$(jq -r '(.context_window.used_percentage // 0) | floor' <<<"$in")
cost=$(jq -r '.cost.total_cost_usd // 0' <<<"$in")
dir=$(jq -r '.workspace.current_dir // "" | split("/") | last' <<<"$in")
vim=$(jq -r '.vim.mode // empty' <<<"$in")
printf '%s | ctx %s%% | $%.2f | %s' "$model" "$pct" "$cost" "$dir"
[ -n "$vim" ] && printf ' | %s' "$vim"
echo
```

Keep it fast (it runs often), never print secrets, and test it by piping sample JSON into it: `echo '{...}' | ~/.claude/statusline.sh`.

## Commands this node introduces

`/statusline` generates a status line; the `statusLine` setting points at your own script.
