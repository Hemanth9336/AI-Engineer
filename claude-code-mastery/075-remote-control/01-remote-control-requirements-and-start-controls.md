---
type: lesson
title: "Remote Control requirements and start controls"
minutes: 14
---

**Remote Control** connects claude.ai/code or the Claude mobile app to a Claude Code session **running on your own machine**. The session keeps your filesystem, MCP servers, tools and project config. The browser or phone is a window onto it. Unlike cloud sessions (topic 076), nothing executes remotely, so your computer must stay on and the `claude` process must keep running.

## Requirements

| Requirement | Detail |
|---|---|
| Plan | Pro, Max, Team or Enterprise. **API keys aren't supported** |
| Sign-in | `/login` with claude.ai |
| Organization | On Team and Enterprise, an Owner must turn on **Remote Control** in Claude Code admin settings (it's off by default). Custom roles need both the cloud sessions permission and the Remote Control permission |
| Provider | Not available on Bedrock, Agent Platform or Foundry, with `ANTHROPIC_BASE_URL` pointing elsewhere, or behind a Claude apps gateway sign-in |
| Environment | `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` (or `DISABLE_GROWTHBOOK`) makes it unavailable |
| Compliance | HIPAA and Zero Data Retention organizations can't enable it |

## Three ways to start

| Mode | Command | Use it for |
|---|---|---|
| **Server mode** | `claude remote-control` | A long-running process that serves sessions you start from claude.ai or the app. Press space for a QR code |
| **Interactive** | `claude --remote-control "My Project"` (or `--rc`) | A normal terminal session that you can also drive remotely |
| **From a running session** | `/remote-control` (or `/rc`) | Publish the conversation you already have, history included |

Useful server-mode flags:

| Flag | Effect |
|---|---|
| `--name "My Project"` | The session title in your list |
| `--spawn same-dir \| worktree \| session` | Sessions share the folder, each get a git worktree, or exactly one session is allowed |
| `--capacity N` | Maximum concurrent sessions (default 32) |
| `--permission-mode acceptEdits` | The starting mode for created sessions |
| `-c`, `--continue`, `--session-id <id>` | Resume a stopped server's sessions (about four hours after it stops) |

Global flags before `remote-control` mostly *don't* carry into the sessions the server creates. Settings that change capability, such as `--settings`, are refused, so configure through settings files.

## Commands this node introduces

`claude remote-control`, `claude --remote-control` (`--rc`), `/remote-control` (`/rc`), `--spawn`, `--capacity`, `--name`, `--continue`, and `--session-id`.
