---
type: lesson
title: "Measuring cost per task"
minutes: 19
---

"Use the smaller model, it's cheaper" is a guess. A fair comparison runs the **same task** on each model and checks every answer. Then you choose the cheapest model that passed **every** case, not the cheapest one per call.

## What the envelope tells you

```bash
claude -p "$prompt" --model haiku --tools "" --output-format json < case.txt > runs/haiku-a.json
jq '{cost: .total_cost_usd, ms: .duration_ms, turns: .num_turns, in: .usage.input_tokens, out: .usage.output_tokens,
     cached: .usage.cache_read_input_tokens, models: (.modelUsage | keys)}' runs/haiku-a.json
```

| Field | Why it matters |
|---|---|
| `total_cost_usd` | The bill for this run, across every model it touched |
| `modelUsage` | Cost and tokens per model. A sonnet run can include cheap haiku calls for background work |
| `usage.input_tokens` and `cache_read_input_tokens` | Input usually dominates agent cost. Cache reads are billed at a fraction of fresh input |
| `usage.output_tokens` | Output tokens cost several times more than input tokens per token |
| `num_turns` | More turns means the context is re-sent more times, which multiplies input cost |
| `duration_ms` | Latency, which matters for interactive and CI paths |

## Rules for a fair comparison

1. **Same input, same prompt, same tools.** Only the model changes.
2. **More than one case**, including a hard one. Small models often tie on easy cases and fall apart on the edge case you actually care about.
3. **Check correctness deterministically** against expected answers, not by eyeballing.
4. **Decide by "cheapest that passes all"**. A model that's 70% cheaper but wrong on one case in ten costs you the rework, or the incident.
5. **Repeat** when a run varies. Average the cost, and require every run to pass.

## Where cost actually comes from

| Lever | Typical effect |
|---|---|
| A smaller model for a narrow step (`--model haiku`, or a haiku subagent) | Large, if quality holds |
| Fewer tools, and a smaller digest as input (topic 061) | Less input per turn |
| `--max-turns`, and a task that finishes in one turn | Fewer re-sends of the context |
| A stable prompt prefix (system prompt, CLAUDE.md) | Cache reads instead of fresh input |
| `--max-budget-usd` | It doesn't reduce cost. It caps the damage of a runaway |

> **This lab VM:** the lab gateway prices its stand-in models identically, so the dollar differences here are small. On a real account, `modelUsage` shows haiku, sonnet and opus at their very different list prices. Your comparison script works unchanged.

## Commands this node introduces

`--model`, `total_cost_usd`, `modelUsage`, `usage.cache_read_input_tokens`, and "cheapest that passes all".
