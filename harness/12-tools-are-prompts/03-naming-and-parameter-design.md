---
type: lesson
title: "Naming and parameter design"
minutes: 6
---

A tool that the model keeps misusing is almost always a tool that was **designed** to be misused: a vague name, free-text parameters where a fixed choice fits, and errors that don't help.

## A tool from a real codebase

```python
{"name": "get", "description": "Get stuff from the monitoring system.",
 "parameters": {"type": "object", "properties": {"q": {"type": "string"}, "t": {"type": "string"}}}}
```

What the model sent in a week of traces:

```text
get(q="billing errors", t="logs")
get(q="search", t="latency yesterday")
get(q="restarts", t="billing")
get(q="p95 for search last 3 days", t="metric")
```

Every call is a reasonable guess. None of them work.

## The redesign

```python
{"name": "get_service_metric",
 "description": "Get one health metric for one Stackline service over the last N hours. Use it for questions "
                "about error rates, latency or restarts. For log lines, use search_logs instead.",
 "parameters": {"type": "object", "properties": {
     "service": {"type": "string", "enum": ["billing", "search"], "description": "The service to measure"},
     "metric": {"type": "string", "enum": ["error_rate", "p95_ms", "restarts"],
                "description": "error_rate = share of failed requests, p95_ms = 95th percentile latency, restarts = count"},
     "window_hours": {"type": "integer", "minimum": 1, "maximum": 168,
                      "description": "How many hours back to look, 1 to 168 (one week). Default 24."}},
   "required": ["service", "metric"]}}
```

## The rules it follows

| Rule | Before | After |
|---|---|---|
| **Name = verb + specific noun** | `get` | `get_service_metric` |
| **One job per tool** | logs, metrics and restarts in one | metrics only; logs elsewhere |
| **Enums for fixed choices** | `t: string` | `metric: enum[error_rate, p95_ms, restarts]` |
| **Typed, bounded numbers** | "last 3 days" as text | `window_hours: integer, 1-168` |
| **Descriptive parameter names** | `q`, `t` | `service`, `metric`, `window_hours` |
| **Explain each value** | nothing | what `p95_ms` means |
| **Point to the right tool** | - | "For log lines, use search_logs" |

## Errors that teach

Even with enums, models sometimes send a value outside them. The error text is the model's next prompt - make it fix the call in one step:

```text
bad:   error: invalid input
good:  error: unknown metric 'latency'. Valid metrics: error_rate, p95_ms, restarts
```

Valid choices in the error message turn a failed call into a correct retry, instead of a loop of guesses.
