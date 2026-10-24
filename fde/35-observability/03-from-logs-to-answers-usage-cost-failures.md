---
type: lesson
title: "From logs to answers: usage, cost, failures"
minutes: 5
---

Once every call is logged, the questions customers and managers ask become queries:

| Question | From the log |
|---|---|
| "What did the assistant cost yesterday?" | Sum of tokens x price per model, for that date |
| "Is it getting slower?" | p95 latency per day |
| "How often does it fail?" | Share of `ok: false`, grouped by `error` |
| "Which model is driving the bill?" | Cost grouped by model |
| "How many people use it?" | Distinct user ids per day |

## Cost from tokens

```text
cost = prompt_tokens x input price / 1,000,000 + completion_tokens x output price / 1,000,000
```

Use the prices in a file (like `prices.json` from topic 4), not hard-coded numbers - they change, and the customer may have negotiated rates.

## Why p95, not the average

Averages hide the slow tail. If 95 requests take 1 second and 5 take 30 seconds, the average is 2.5 s - "fine" - while one user in twenty waits half a minute. **p95** is the value 95% of requests are faster than. A simple, exact definition (nearest rank):

```python
latencies = sorted(values)
p95 = latencies[math.ceil(0.95 * len(latencies)) - 1]
```

## Make it a habit

A daily report - calls, errors, cost, p95, by model - takes twenty lines of Python and answers most of the questions you'll be asked during a pilot. Send it to the customer's project lead every morning. Trust grows fastest when they see the numbers before they ask for them.
