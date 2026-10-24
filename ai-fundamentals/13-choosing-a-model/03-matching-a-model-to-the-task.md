---
type: lesson
title: "Matching a model to the task"
minutes: 7
---

Choosing a model is an engineering trade-off between **quality**, **speed**, and **cost**. Here is a practical way to decide.

## Start from the task

| Task | Good starting point | Why |
|---|---|---|
| Label tickets as bug / question / outage | Small | Simple, short output, often millions of calls |
| Extract fields into JSON | Small or mid | Pattern-following, not deep thought |
| Summarize a document for a team | Mid | Needs fluency, not deep reasoning |
| Review a complex pull request | Large | Subtle bugs need capability |
| Plan a migration with dependencies | Reasoning | Multi-step logic |
| Chat assistant users wait on | Mid, fast | Latency matters as much as quality |

## The cheapest model that passes

The method professionals use:

1. Write a handful of **test inputs** with known good answers.
2. Run them on a **mid** model. Does it pass?
3. If yes, try the **smaller** model. Still passing? Use it.
4. If no, try a **larger** or **reasoning** model.

Choose the cheapest model that meets your bar, and re-run the tests when models update.

## Cost compounds at scale

One request costs fractions of a cent, so it is tempting to always use the best model. But:

```text
1,000,000 tickets x 500 input tokens = 500M input tokens
small model at $0.10 / 1M  ->      $50
large model at $3.00 / 1M  ->   $1,500
```

Same job, 30x the price. For a batch job that runs every day, that difference matters.

## Mix models in one system

Real applications often use several: a small model **routes** or classifies each request, and only the hard ones go to a large model. Coding assistants do the same - a fast model for autocomplete, a strong one for agent work.

## Measure, don't guess

Compare candidates on the same prompt and look at three things: the **answer quality**, `usage.completion_tokens` (cost and length), and how long it took (`curl -w '%{time_total}'`). Now try it.
