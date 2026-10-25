---
type: lesson
title: "Streaming a run as JSON events"
minutes: 12
---

`--output-format json` gives you one object at the **end**. For a long run you want to see it happen - and for a gate you want to know whether it **finished** at all.

```bash
claude -p "Run the tests and report" --output-format stream-json --verbose > stream.jsonl
```

In print mode `stream-json` **requires `--verbose`**; without it claude refuses to start: `Error: When using --print, --output-format=stream-json requires --verbose`.

## The events, one per line

| `type` | `subtype` | Carries |
|---|---|---|
| `system` | `init` | Model, tools, MCP servers (and `mcp_server_errors`), permission mode, session id |
| `assistant` | - | A model message: text blocks and `tool_use` blocks |
| `user` | - | Tool results going back to the model |
| `result` | `success` / `error_*` | The same run object as `--output-format json` - **always last** |

Add `--include-partial-messages` for token-by-token `stream_event` lines (for live UIs), `--include-hook-events` for hook lifecycle events.

## Watching it live

```bash
claude -p "$prompt" --output-format stream-json --verbose \
  | tee stream.jsonl \
  | jq --unbuffered -r 'select(.type == "assistant") | .message.content[] | select(.type == "tool_use") | "-> \(.name)"'
```

`tee` keeps the full record; `jq --unbuffered` prints each tool call as it happens.

## The one rule

The `result` event is the only proof that the run **ended**. A stream that stops without one was killed, timed out, or crashed - whatever the last assistant message said. Never take the last text you saw as the answer.

## Commands this node introduces

`--output-format stream-json --verbose`, `--include-partial-messages`, `--include-hook-events`, and `jq --unbuffered` for live progress.
