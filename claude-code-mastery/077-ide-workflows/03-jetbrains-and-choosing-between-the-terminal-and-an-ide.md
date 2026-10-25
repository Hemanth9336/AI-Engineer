---
type: lesson
title: "JetBrains, and choosing between the terminal and an IDE"
minutes: 14
---

## JetBrains

The **Claude Code [Beta]** plugin works with IntelliJ IDEA, PyCharm, WebStorm, GoLand, PhpStorm and Android Studio.

- It **doesn't bundle the CLI**. Install `claude` separately and make sure the plugin's **Claude command** setting finds it.
- Launch with `Cmd+Esc` / `Ctrl+Esc` or the Claude button. Diffs open in the IDE's diff viewer (`/config` > **Diff tool**: `auto` or `terminal`).
- From an external terminal, run `/ide` **from the project root**. Success prints `Connected to IntelliJ IDEA.`
- Its IDE MCP server exposes only `mcp__ide__getDiagnostics`, one file per call. Claude doesn't fetch diagnostics automatically after edits, so ask it to check them, or say so in `CLAUDE.md`.
- With Remote Development, install the plugin on the **remote host**.
- Leave **Accept connections from all network interfaces** off unless loopback can't work. The transport is unencrypted, so the token would cross your network in cleartext.
- In `acceptEdits` mode, Claude can edit IDE configuration files that the IDE may execute. Prefer Manual mode in projects with run configurations you don't control.

## Choosing a surface

| Work | Best surface | Why |
|---|---|---|
| Careful edits you want to see and approve hunk by hunk | **IDE** | Native diffs, inline plan comments, selection mentions |
| Refactors guided by compiler errors | **IDE** (or CLI in the integrated terminal) | Diagnostics through `getDiagnostics` |
| Scripting, `-p`, pipelines, many parallel sessions, tmux | **Terminal** | Every command and flag, `!` shell, background sessions |
| Remote servers over SSH | **Terminal** (plus `/ide` if the IDE is on that host) | Nothing to install beyond the CLI |
| Long unattended tasks | **Cloud session** (topic 076) | Keeps running without your machine |

The surfaces share history and settings, so switching is cheap. Start in the terminal, `/ide` to review diffs, and `claude --resume` in the panel.

## Commands this node introduces

The Claude Code [Beta] plugin, the **Claude command** setting, `Cmd+Esc`, `/ide` from the project root, the **Diff tool** setting, and choosing a surface by the kind of work.
