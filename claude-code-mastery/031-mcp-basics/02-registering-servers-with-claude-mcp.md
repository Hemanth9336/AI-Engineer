---
type: lesson
title: "Registering servers with claude mcp"
minutes: 14
---

```bash
claude mcp add handbook -- mcp-server-filesystem /root/mastery/031-mcp/handbook       # stdio, local scope
claude mcp add --scope project handbook -- mcp-server-filesystem ./handbook           # shared in .mcp.json
claude mcp add --transport http tracker https://mcp.example.com/mcp                   # remote server
claude mcp list        # every server with a health check
claude mcp get handbook
claude mcp remove handbook
```

Everything after `--` is the command Claude Code runs to start the server.

## Scopes

| Scope | Stored in | Use |
|---|---|---|
| `local` (default) | `~/.claude.json`, under this project | Just you, just here |
| `project` | `.mcp.json` in the repo root | The whole team - commit it |
| `user` | `~/.claude.json`, top level | You, in every project |

Servers from a repository's `.mcp.json` start as **pending approval** - `claude mcp list` says so, and `claude` asks each teammate the first time. `"enabledMcpjsonServers": ["handbook"]` in `.claude/settings.local.json` approves named servers for you; `enableAllProjectMcpServers` approves all of them (use it only for repositories you control).

## In headless runs

- MCP tools need permission like any tool: `--allowedTools "mcp__handbook__read_text_file,mcp__handbook__list_directory"` (or `mcp__handbook__*` for all of a server's tools).
- `--mcp-config ci-mcp.json` loads servers from a file for one run; add `--strict-mcp-config` to ignore every other configured server - reproducible CI.

## In the console

`/mcp` lists servers with their status and tools, and handles sign-in for remote servers that use OAuth. `@handbook:` mentions resources a server exposes.

## Commands this node introduces

`claude mcp add / list / get / remove`, `--scope`, `--allowedTools mcp__...`, `--mcp-config`, `--strict-mcp-config`, and `/mcp`.
