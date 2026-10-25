---
type: lesson
title: "Log the full trajectory"
minutes: 6
---

When an agent gets something wrong, the first question is always "what did it actually do?" A final answer can't tell you. A **transcript** can: a complete, ordered record of everything the harness sent, received and executed.

## What a transcript records

One JSON line per event, all sharing a **run ID**:

| Event | Fields |
|---|---|
| `run_start` | task, model, system prompt |
| `model_call` | step, model, number of messages sent, prompt/completion tokens, latency, finish reason, the text and tool calls that came back |
| `tool_call` | step, tool name, arguments, the **full** result, whether it was an error |
| `run_end` | status (`done`, `max_steps`, `error`), answer, steps, total tokens |

```json
{"type": "tool_call", "run_id": "20260314-091502-a41f0c", "ts": 1773479703.2, "step": 1,
 "name": "read_file", "args": {"path": "services/billing.yaml"}, "result": "name: billing\n...", "error": false}
```

## Why each field earns its place

- **Run ID** - ties every line of one run together, even when parallel subagents write at the same time (topic 26).
- **Step** - lets you line up what the model asked for with what it got.
- **Full tool results** - most agent bugs are in what the model **saw**, not what it said.
- **Tokens and latency** - per call, so cost and slowness can be traced to a step (topic 32).
- **Finish reason** - `tool_calls`, `stop`, `length` (cut off) tell you why a call ended.

## Transcripts vs traces vs logs

| | Contains | Used for |
|---|---|---|
| Trace (topic 30) | Tool names and arguments | Grading step checks |
| **Transcript** | Everything, in order | Debugging, replay, cost analysis |
| Ops logs | Metadata only | Dashboards and alerts |

Transcripts contain whatever the tools returned - customer data, file contents. Store them where access is controlled, redact secrets on the way in (topic 24), and keep them as long as you need for debugging, not forever.

## Replay

With the full transcript you can **replay** a run: rebuild the message list up to step N from the recorded events, change one thing - the system prompt, a tool result, the model - and call the model from there. That turns "it failed once in production" into a reproducible experiment.
