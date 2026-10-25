---
type: lesson
title: "Hooks and hook events"
minutes: 14
---

Permission rules decide **whether** a tool call may run. **Hooks** run **your code** at fixed points around it - the model cannot skip them, because Claude Code runs them, not the model. Fundamentals showed a first hook; this topic is the full map.

## The events you will use most

| Event | Fires | Can block? | Typical use |
|---|---|---|---|
| `SessionStart` | A session starts, resumes, clears, or compacts | No | Load context, set env vars |
| `UserPromptSubmit` | Before Claude sees your prompt | Yes | Reject or enrich prompts |
| `PreToolUse` | Before a tool call runs | Yes | Guardrails, input rewriting |
| `PermissionRequest` | When a permission prompt would show | Yes | Auto-approve or deny for scripts |
| `PostToolUse` | After a tool call **succeeds** | Feedback only | Format, lint, test, audit |
| `PostToolUseFailure` | After a tool call fails | Feedback only | Log failures |
| `Stop` / `SubagentStop` | Claude (or a subagent) finishes its turn | Yes - sends it back to work | "Tests must pass before you stop" |
| `PreCompact`, `Notification`, `SessionEnd` | Compaction, alerts, exit | No | Save state, notify, clean up |

## Anatomy of a hook config

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/audit.py\"", "timeout": 10 }
        ]
      }
    ]
  }
}
```

Event, then **matcher groups**, then **handlers**. All matching handlers for an event run **in parallel**, and an identical handler defined in two settings files runs once.

## Matchers

| Matcher | Means |
|---|---|
| omitted, `""`, `"*"` | Every tool |
| `Bash`, `Write|Edit`, `Write, Edit` | Exact tool names (only letters, digits, `_ - , |` and spaces) |
| anything else, e.g. `mcp__records__.*`, `^Notebook` | A JavaScript regex, **unanchored** - `Edit.*` also matches `NotebookEdit` |

For finer filtering, a handler's `if` field takes **one** permission rule: `"if": "Bash(git *)"` or `"if": "Edit(*.ts)"`.

## Where hooks live

User, project, and local settings files, plugins (`hooks/hooks.json`), and the frontmatter of skills and agents (scoped to while they run). `/hooks` shows everything that is active and where it came from; `"disableAllHooks": true` turns them off.

## Handler types

`command` (a script - most common), `http` (POST the event to a URL), `mcp_tool` (call an MCP tool), `prompt` (a one-shot model judgement), and `agent` (a subagent that can read files before deciding).

## Two traps

- `PostToolUse` fires only for **successful** calls - failures go to `PostToolUseFailure`.
- A matcher on `Write|Edit` does **not** fire when a `Bash` command rewrites the file. Audit by tool, or watch the disk with `FileChanged`.

## Commands this node introduces

`/hooks` to inspect active hooks; the `hooks`, `matcher`, `if`, and `disableAllHooks` settings.
