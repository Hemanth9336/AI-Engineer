---
type: lesson
title: "Reading the usage block in detail"
minutes: 7
---

Every chat completion response ends with a `usage` object. It is the ground truth for cost and context size.

## The basic fields

```json
"usage": {
  "prompt_tokens": 412,
  "completion_tokens": 96,
  "total_tokens": 508
}
```

| Field | Meaning |
|---|---|
| `prompt_tokens` | Every token you sent: system, all history, the new user message, tool definitions |
| `completion_tokens` | Every token the model generated, including hidden reasoning |
| `total_tokens` | The sum of the two |

## The detail fields

Many providers add breakdowns:

```json
"prompt_tokens_details":     {"cached_tokens": 256},
"completion_tokens_details": {"reasoning_tokens": 64}
```

- `cached_tokens` - input tokens served from the prompt cache, billed at a discount.
- `reasoning_tokens` - thinking tokens from reasoning models: billed, but not visible in the reply.

Not every provider fills these in; treat them as optional (`// 0` in jq).

## Read it with jq

```bash
jq '.usage' response.json
jq -r '"in=\(.usage.prompt_tokens) out=\(.usage.completion_tokens)"' response.json
```

## The Messages API names them differently

The Anthropic-style `/v1/messages` endpoint reports `input_tokens` and `output_tokens` instead. Same idea, different keys - check which API you called before you parse.

## Why prompt_tokens surprises people

`prompt_tokens` is often larger than you expect, because it includes:

- the whole conversation history (topic 12),
- the system message,
- any tool definitions (topic 16) - each one is serialized into the prompt,
- a few tokens of formatting per message.

## In the lab

The gateway records token counts for every call, so you can watch them without saving responses:

```bash
ailab log 5
jq -s 'map(.total_tokens) | add' /var/log/ailab/requests.jsonl    # all tokens used so far
```
