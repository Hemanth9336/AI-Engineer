---
type: lesson
title: "Cowork, Dispatch, and the two places configuration lives"
minutes: 14
---

## Cowork and Dispatch

- **Cowork** is the Desktop surface for longer agentic work that isn't only code: research, documents, spreadsheets.
- **Dispatch** is a persistent Cowork conversation you hand tasks to, from the desktop or your phone. For code tasks (a bug, a dependency bump, tests, a PR) it can **spawn a Code session**, which appears in the Code sidebar. Other work stays in Cowork. You get a push notification when it finishes or needs approval. Dispatch is available on Pro and Max, not on Team or Enterprise.

## Two places configuration lives

| Lives in | What | Shared with the CLI? |
|---|---|---|
| **Local files** | `CLAUDE.md`, `CLAUDE.local.md`, `~/.claude/settings.json`, the project's `.claude/`, `.mcp.json`, `~/.claude.json` | **Yes**. The Code tab and the CLI read the same files |
| **Your claude.ai account (Customize)** | Connectors, skills and plugins enabled in the app | Synced across devices. Cowork uses these, *not* `~/.claude`. Terminal sessions signed in to the same account also load the account's enabled skills and plugins |
| **Desktop only** | Saved environments, encrypted environment variables, Settings > Claude Code (browser tools, worktree location, auto-archive), and MCP servers from `claude_desktop_config.json` (local Code sessions only; copy them into the CLI with `claude mcp add-from-claude-desktop`) | No |

When something works in the terminal but not in Desktop, or the other way round, the first question is which of these places the configuration lives in.

Admins control Desktop through the admin console (the Desktop, Cloud sessions and Remote Control toggles) and through Desktop's own managed settings. That file is different from Claude Code's `managed-settings.json`: on Linux it's `/etc/claude-desktop/managed-settings.json`.

## What Desktop doesn't do

Agent teams (CLI only), scripting with `-p` and output formats, and `/resume` of SSH, WSL or cloud sessions from the CLI. Use the terminal for automation, and Desktop for visual, interactive, parallel work.

## Commands this node introduces

Cowork, Dispatch, Customize (account-synced configuration), `claude_desktop_config.json`, `claude mcp add-from-claude-desktop`, and Desktop's managed settings.
