---
type: lesson
title: "The extension settings and the built-in IDE MCP server"
minutes: 14
---

## Settings worth knowing (Extensions > Claude Code)

| Setting | Default | Why it matters |
|---|---|---|
| `autosave` | `true` | Saves files before Claude reads or writes them. Turn it off and Claude may work against stale disk contents while your unsaved buffer differs |
| `initialPermissionMode` | unset | The starting mode. It's read from **user** settings only; workspace values are ignored, so a repo can't start you in bypass |
| `allowDangerouslySkipPermissions` | `false` | Adds Bypass to the mode list. "Use it only in sandboxes with no internet access." |
| `respectGitIgnore` | `true` | Withholds selections from gitignored files in the panel |
| `attachOpenFile` | `true` | Sends the open file as context |
| `useTerminal` | `false` | Runs the CLI in a terminal instead of the panel |
| `environmentVariables` | `[]` | Env for the extension's Claude process |

Shared Claude Code settings (permissions, hooks) still come from `~/.claude/settings.json` and the project's `.claude/settings.json`.

## The IDE MCP server

When the extension runs, it hosts a local MCP server named `ide` (hidden from `/mcp`). The CLI connects to it automatically. It's how diffs open natively, and how Claude reads what your editor knows:

| Tool | What | Notes |
|---|---|---|
| `mcp__ide__getDiagnostics` | Language-server errors and warnings from the Problems panel, for one file or all | Read-only. The fastest way for Claude to check its own edit compiled |
| `mcp__ide__executeCode` | Run Python in the active Jupyter kernel | Always asks with a VS Code Quick Pick, even if allowed |

- It binds to `127.0.0.1` on a random port with a per-activation token in `~/.claude/ide/<port>.lock`.
- To block diagnostics sharing, deny `mcp__ide__getDiagnostics` (and the panel's `mcp__claude-vscode__getDiagnostics`). A `Read` deny doesn't cover them, but it does block selections and open-file context for matching paths.

## Commands this node introduces

`autosave`, `initialPermissionMode`, `allowDangerouslySkipPermissions`, `respectGitIgnore`, the `ide` MCP server, `mcp__ide__getDiagnostics`, and `mcp__ide__executeCode`.
