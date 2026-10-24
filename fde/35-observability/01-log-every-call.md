---
type: lesson
title: "Log every call"
minutes: 5
---

When the customer says "the bot gave a weird answer yesterday around ten", you need to find that exact request - the question, the model, the prompt version, what was retrieved, how long it took, what it cost. If it isn't logged, it didn't happen.

## One line per model call

Wrap every model call in one function that writes a JSON line, success or failure:

```json
{"ts": "2026-03-14T10:02:11+00:00", "request_id": "6f1c...", "model": "lab-fast", "question": "Can I change my address?",
 "ok": true, "error": null, "prompt_tokens": 812, "completion_tokens": 64, "latency_ms": 1430}
```

| Field | Answers |
|---|---|
| `ts`, `request_id` | When, and which one - the id ties together logs from retrieval, tools and the UI |
| `model` | What it cost, and which model to blame |
| `prompt_tokens`, `completion_tokens` | Cost and context size |
| `latency_ms` | Speed, timeouts, p95 |
| `ok`, `error` | Failure rate and why |
| `question` (truncated) | What users actually ask |

In a real system add: user or tenant id, prompt version, retrieved chunk ids and scores, tool calls, and the final answer.

## Log failures too

The `try / except / finally` pattern makes sure a line is written even when the call raises - and the exception still propagates. A log of successes only hides exactly the incidents you'll be asked about.

## Mind what you log

Prompts and answers can contain personal data. Agree with the customer what's logged, where it's stored, who can read it and how long it's kept (topic 36). Often the answer is: metadata always, full text redacted or sampled, with a retention limit.

## Use what you have

In production, an observability tool (Langfuse, LangSmith, OpenTelemetry-based tracing, or the customer's own logging stack) gives you search and dashboards. The idea is the same: one structured record per call, linked by request id.
