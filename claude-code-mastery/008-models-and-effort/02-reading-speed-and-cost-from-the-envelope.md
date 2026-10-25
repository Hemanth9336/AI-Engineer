---
type: lesson
title: "Reading speed and cost from the envelope"
minutes: 14
---

"Haiku is faster" is a guess until you measure it on *your* task. The JSON envelope gives you the numbers for free.

| Field | Means |
|---|---|
| `duration_ms` | Wall-clock time for the whole run |
| `duration_api_ms` | Time spent waiting on the model |
| `num_turns` | Loop iterations - more turns, more cost |
| `total_cost_usd` | Estimated cost of the run |
| `usage.input_tokens`, `usage.output_tokens` | Tokens for the run |
| `modelUsage` | The same numbers broken down per model (useful when a run uses more than one) |

```bash
claude -p "$PROMPT" --model haiku  --output-format json > haiku.json
claude -p "$PROMPT" --model sonnet --output-format json > sonnet.json
jq -r '"\(.duration_ms) ms  $\(.total_cost_usd)  \(.num_turns) turns  \(.modelUsage|keys|join(","))"' haiku.json sonnet.json
```

## Read the numbers honestly

- **One run is an anecdote.** Latency varies; for a real decision, run each model several times and compare medians.
- **Cost is an estimate** computed by the client from token counts; your bill is the source of truth.
- **Quality is not in the envelope.** A cheap wrong answer is expensive. Check that both outputs are correct before comparing price.
- **Check which model answered.** `modelUsage` keys name the model that actually ran - the proof that your `--model` flag took effect.

## Commands this node introduces

`jq` string interpolation (`"\(.field)"`) prints several envelope fields on one line.
