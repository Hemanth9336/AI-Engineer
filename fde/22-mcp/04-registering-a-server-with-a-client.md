---
type: lesson
title: "Registering a server with a client"
minutes: 6
---

A client needs to know how to **start** each stdio server: the command and its arguments. Every MCP client has a configuration for this. In Claude Code it's the `claude mcp` command:

```bash
claude mcp add --scope user meridian -- python /root/fde-lab/22-mcp/server.py
claude mcp list          # shows each server and whether it connected
claude mcp remove --scope user meridian
```

- `meridian` is the name you give the server.
- Everything after `--` is the command Claude Code runs to start it.
- `--scope user` makes it available in every folder; the default scope is the current project only.
- Use **absolute paths**: the client may start the server from any directory, with a different `PATH`. `$(command -v python)` gives the absolute path of the Python you're using - the one with the `mcp` package installed.

## Tool names in the client

Claude Code shows MCP tools to the model as `mcp__<server>__<tool>` - here `mcp__meridian__track_parcel` - so tools from different servers can't collide.

## Permissions

Claude Code asks before using a tool it hasn't been allowed to use. In non-interactive mode (`claude -p`) there's nobody to ask, so you allow tools up front:

```bash
claude -p "Where is order MER-55120? Use the meridian tool." --allowedTools mcp__meridian__track_parcel
```

Allow exactly the tools the task needs - not every tool. That's the same least-privilege rule you'd apply to any integration.

## Other clients

Cursor, VS Code, Claude Desktop and most agent frameworks use a JSON config with the same information:

```json
{"mcpServers": {"meridian": {"command": "/root/ai-lab/.venv/bin/python", "args": ["/root/fde-lab/22-mcp/server.py"]}}}
```

Same server, different client - which is the whole point of the standard.
