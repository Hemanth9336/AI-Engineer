---
type: lesson
title: "Loops multiply cost"
minutes: 6
---

A single chat call has a cost you can estimate on a napkin. An agent run doesn't, because every step **re-sends the whole history**. Cost grows faster than the number of steps.

## Why it compounds

```text
step 1: system + tools + task                          ~   900 tokens in
step 2: ... + call 1 + result 1 (a log file)           ~ 2,350
step 3: ... + call 2 + result 2                        ~ 3,800
step 4: ...                                            ~ 5,250
step 5: ...                                            ~ 6,700
```

Five steps, but the input tokens add up to ~19,000 - not 5 x 900. Each tool result is paid for on **every later step**. A 4,000-token log read at step 2 of a 10-step run is billed eight times.

## Reading cost from a transcript

With per-call usage in the transcript (topic 31) and a price table, cost is arithmetic:

```python
usd = (prompt_tokens * price_in + completion_tokens * price_out) / 1_000_000
```

| What to compute | Why |
|---|---|
| **Total per run** | The number for budgets and pricing |
| **By model** | A cheap summarizer call (compaction) vs the main model |
| **By step** | Which step was the expensive one - usually the one after the biggest tool result |
| **Input vs output** | Agents are input-heavy: often 95%+ of tokens are input |

## Latency compounds too

Each step is a round trip: model latency (often 1-5 seconds) plus tool time. Ten steps is 10-50 seconds before the user sees anything. The same levers help both cost and latency: fewer steps, smaller results, a cheaper model for easy calls, parallel subagents for independent reads (topic 26).

## The biggest levers, in order

1. **Smaller tool results** - trim, paginate, point to files (topic 13).
2. **Fewer steps** - better tool descriptions and tool sets (topics 12, 14).
3. **Context management** - budgets and compaction (topics 17, 18).
4. **Model routing** - a cheaper model for summaries, classification, verification.
5. **Prompt caching** - a stable prefix is billed at a discount (topic 20).
