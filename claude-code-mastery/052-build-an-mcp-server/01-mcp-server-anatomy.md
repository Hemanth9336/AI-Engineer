---
type: lesson
title: "MCP server anatomy"
minutes: 19
---

Topics 031-033 *used* MCP servers, and 033 built one with the Python SDK's `FastMCP`. This topic removes the SDK so you can see the protocol itself. That is what you'll be debugging when a server "connects but has no tools".

## The stdio transport

Claude Code starts the server as a child process and talks to it over **stdin and stdout**: one JSON-RPC 2.0 message per line, UTF-8, newline-terminated.

- **stdout is the protocol.** A stray `print("starting...")` corrupts the stream, and the client drops the connection.
- **stderr is your log.** Claude Code captures it; `claude --debug` shows it.
- The server lives as long as the session. Read lines in a loop until stdin closes.

## The lifecycle

```text
client → {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{...}}}
server ← {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18","capabilities":{"tools":{}},"serverInfo":{"name":"wordcount","version":"1.0.0"}}}
client → {"jsonrpc":"2.0","method":"notifications/initialized"}          (a notification: no id, and no reply)
client → {"jsonrpc":"2.0","id":2,"method":"tools/list"}
server ← {"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"count_words","description":"...","inputSchema":{...}}]}}
client → {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"count_words","arguments":{"text":"a b c"}}}
server ← {"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"{\"words\": 3, ...}"}],"structuredContent":{"words":3,...},"isError":false}}
```

| Piece | Rule |
|---|---|
| Version negotiation | Echo the client's `protocolVersion` if you support it; otherwise answer with the newest one you do support |
| `capabilities` | Declare `tools` (and `resources` or `prompts` if you serve them). Clients only ask for what you declare |
| Tool definition | `name`, `description` (the model reads it, so write it like a skill description), `inputSchema` (JSON Schema), and optionally `outputSchema` |
| Tool result | `content` is a list of blocks (`text`, `image`, ...). `structuredContent` carries machine-readable output matching `outputSchema` |
| Notifications | Any message without an `id`. Never reply to one |

## Two kinds of error

| Situation | Reply | Who sees it |
|---|---|---|
| Unparsable line | `error` with code `-32700` (parse error) | The client |
| Unknown method | `error` `-32601` (method not found) | The client |
| Unknown tool, or invalid params | `error` `-32602` (invalid params) | The client |
| The tool ran and failed, or the input was wrong | A **result** with `isError: true` and a text explanation | **The model**, which can correct itself and retry |

The last row matters most: a protocol error looks to Claude like a broken server, while `isError: true` reads like useful feedback.

## Registering it with Claude Code

```bash
claude mcp add --scope project wordcount -- python3 wordcount_server.py     # writes .mcp.json
echo '{"enabledMcpjsonServers": ["wordcount"]}' > .claude/settings.local.json # approve it for yourself
claude -p "..." --allowedTools mcp__wordcount__count_words --output-format stream-json --verbose < /dev/null
```

Tools appear to Claude as **`mcp__<server>__<tool>`**. That name is what you put in `--allowedTools`, permission rules, and hook matchers. The `system`/`init` event in stream-json lists each server with its `status`, which is the quickest way to tell "didn't connect" from "connected, but the tool wasn't allowed".

## Commands this node introduces

The newline-delimited JSON-RPC stdio transport, `initialize`, `notifications/initialized`, `tools/list`, `tools/call`, the error codes `-32700`, `-32601`, and `-32602`, `isError`, `structuredContent`, and `mcp__<server>__<tool>`.
