---
type: lesson
title: "Measuring runs with time and JSON usage fields"
minutes: 9
---

Measure instead of guessing. Every `claude -p --output-format json` run already reports what you need.

| Field | Meaning |
|---|---|
| `duration_ms` | Wall time of the run as Claude Code saw it |
| `duration_api_ms` | Time spent waiting on the model |
| `num_turns` | Turns in the loop |
| `total_cost_usd` | Estimated spend at list price |
| `usage.input_tokens`, `usage.output_tokens` | Uncached input and output tokens |
| `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens` | Cached input read and written |
| `modelUsage` | The same numbers per model, keyed by model ID - it can list a second, smaller model used for background work |

Add a wall clock you control, so startup is included:

```bash
TIMEFORMAT=%R                      # bash's time keyword prints just the seconds
wall=$( { time claude -p "$P" --model haiku --output-format json < /dev/null > run.json 2>/dev/null; } 2>&1 )
jq -r --arg w "$wall" '[$w, .duration_ms, .num_turns, .total_cost_usd] | @csv' run.json
```

(`/usr/bin/time -p` works too where it is installed. The bash keyword is always there.)

## Measure like you mean it

- **Same prompt, same repo state, same tools** for every run. Change only `--model`.
- **Several runs per model.** One run is an anecdote: models are not deterministic, and latency varies. Three is a minimum, report the **median**.
- **An oracle for correctness.** Compute the right answer independently - a test suite, or a few lines of code - and score each run pass or fail. A fast wrong answer is not cheap, it is waste.
- **Bound every run** with `--max-turns` so one runaway doesn't distort the totals.
- **Record raw data** (one JSON file per run, one CSV row per run) and summarize separately, so the summary can be re-computed and checked.

## Commands this node introduces

`TIMEFORMAT=%R` with `time`, `duration_api_ms`, `modelUsage`, and jq's `@csv`.
