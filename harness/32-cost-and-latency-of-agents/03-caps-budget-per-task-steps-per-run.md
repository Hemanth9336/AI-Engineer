---
type: lesson
title: "Caps: budget per task, steps per run"
minutes: 6
---

Topic 8's step limit stops a loop that never ends. It doesn't stop a loop that ends after 8 steps - each carrying 30,000 tokens. You need a cap on **what you actually pay for**: tokens.

## Three caps, three jobs

| Cap | Stops | Typical value |
|---|---|---|
| **Max steps** | Loops that never finish | 8-30 |
| **Token budget per task** | Expensive runs: big results, long histories | Measured from your evals: p95 x 2 |
| **Wall-clock timeout** | Hung tools, slow providers | A few minutes |

Plus caps above the task: per user per day, per tenant per month, and a hard monthly spend limit at the provider.

## Enforce the budget before the call

Checking after the call is too late - you've already paid. Before each call, estimate what it will cost and stop if it would cross the budget. The next call's input is at least the last call's input (history only grows), which makes a simple, safe estimate:

```python
if spent and spent + last_prompt_tokens > budget:
    return f"stopped: token budget reached ({spent} of {budget} tokens used)"
resp = client.chat.completions.create(...)
spent += resp.usage.prompt_tokens + resp.usage.completion_tokens
last_prompt_tokens = resp.usage.prompt_tokens
```

- Count **actual** usage from the API, not your own estimate.
- Count **every** call that belongs to the task: subagents, verifiers and compaction too.
- Stop with a clear status and a distinct exit code, so callers can tell "out of budget" from "done" and "failed".

## Choosing the number

Run your eval suite and look at the token totals per task. Set the budget well above the normal range (p95 x 2 is a reasonable start) so it only stops runaway runs. A budget that stops good runs isn't a safety net, it's a bug.

## What to do when a budget hits

- Tell the user what was done and what wasn't: partial results beat silence.
- Save state so the task can resume with a new budget, after a human decides (topic 19).
- Log it. A budget that hits often is a signal: a tool returns too much, or a prompt makes the agent wander.
