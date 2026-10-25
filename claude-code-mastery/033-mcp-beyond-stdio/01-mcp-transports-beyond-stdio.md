---
type: lesson
title: "MCP transports beyond stdio"
minutes: 12
---

A stdio server is a process Claude Code starts on your machine. Most company and SaaS servers are **remote**: they already run somewhere, and Claude Code connects to a URL.

| Transport | Add with | Use when |
|---|---|---|
| `stdio` | `claude mcp add <name> -- <command> [args]` | Local tools, scripts, anything that needs your files |
| `http` (streamable HTTP) | `claude mcp add --transport http <name> <url>` | **The default for remote servers** - supports OAuth |
| `sse` | `claude mcp add --transport sse <name> <url>` | Older servers that only offer Server-Sent Events (deprecated) |
| `ws` (WebSocket) | `claude mcp add-json <name> '{"type":"ws","url":"wss://..."}'` | Servers that push events unprompted; header auth only |

```bash
claude mcp add --transport http tracker https://mcp.example.com/mcp --header "Authorization: Bearer $TRACKER_TOKEN"
claude mcp add --transport sse legacy https://legacy.example.com/sse
claude mcp add-json events '{"type":"ws","url":"wss://events.example.com/socket"}'
```

Recent versions try HTTP first and fall back to SSE on their own when a server only speaks SSE.

## In JSON

```json
{
  "mcpServers": {
    "tracker": { "type": "http", "url": "${TRACKER_URL:-https://mcp.example.com}/mcp",
                 "headers": { "Authorization": "Bearer ${TRACKER_TOKEN}" } }
  }
}
```

- An entry with a `url` but no `type` is an **error** - Claude Code would read it as stdio. Always set `type`.
- `${VAR}` and `${VAR:-default}` expand in `command`, `args`, `env`, `url`, and `headers`, so a committed `.mcp.json` carries no secrets.
- Claude Code refuses to expand its own credentials (such as `ANTHROPIC_AUTH_TOKEN`) into a remote server's URL or headers.

## Sign-in

Servers that use OAuth show **needs authentication** in `claude mcp list`; run `/mcp` in the console to sign in. Tokens are stored for you and refreshed automatically.

## Commands this node introduces

`claude mcp add --transport http|sse`, `--header`, `claude mcp add-json`, and `${VAR}` expansion in `.mcp.json`.
