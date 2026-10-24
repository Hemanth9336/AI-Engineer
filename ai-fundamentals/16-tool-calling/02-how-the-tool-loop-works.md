---
type: lesson
title: "How the tool loop works"
minutes: 8
---

A tool call takes **two requests** (or more). Here is the exact message flow in the chat completions API.

## Request 1: question plus tools

```json
{"model": "lab-fast",
 "messages": [{"role": "user", "content": "Is checkout healthy?"}],
 "tools": [ { "type": "function", "function": { "name": "get_service_status", ... } } ]}
```

## Response 1: a tool call, not an answer

```json
"choices": [{
  "finish_reason": "tool_calls",
  "message": {
    "role": "assistant",
    "content": null,
    "tool_calls": [{
      "id": "call_8f2k",
      "type": "function",
      "function": {"name": "get_service_status", "arguments": "{\"service\": \"checkout\"}"}
    }]
  }
}]
```

Two details trip people up:

- `finish_reason` is `tool_calls`, and `content` is usually `null`.
- `arguments` is a **string** containing JSON, not a JSON object. Parse it: `jq -r '.arguments | fromjson | .service'`.

## Your code runs the tool

Read the name and arguments, run the real function, and capture the result - usually as a small JSON string.

## Request 2: history plus the result

Send the original messages, **plus** the assistant message from response 1 exactly as you received it, **plus** a `tool` message carrying the result:

```json
"messages": [
  {"role": "user", "content": "Is checkout healthy?"},
  {"role": "assistant", "content": null, "tool_calls": [ {"id": "call_8f2k", ...} ]},
  {"role": "tool", "tool_call_id": "call_8f2k", "content": "{\"status\": \"degraded\", \"error_rate\": \"4.2%\"}"}
]
```

The `tool_call_id` must match the `id` from the tool call - that is how the model pairs results with requests. Include the same `tools` list again.

## Response 2: the answer

Now `finish_reason` is `stop` and `content` is the final answer, written from the tool's result.

## Loops and parallel calls

- The model may call **several tools at once** (several entries in `tool_calls`) - answer each with its own `tool` message.
- It may call another tool after seeing a result. Keep looping until `finish_reason` is `stop` - with a maximum number of rounds, so a confused model cannot loop forever.

## Control knobs

`"tool_choice": "auto"` (default) lets the model decide; `"required"` forces a call; `"none"` forbids one; naming a function forces that tool. Next, run the loop by hand with `curl` and `jq`.
