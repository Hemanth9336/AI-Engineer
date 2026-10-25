---
type: lesson
title: "Structured output from headless runs"
minutes: 14
---

`claude -p` is how Claude Code becomes a building block in scripts, CI jobs, and other programs. Fundamentals used it; here you treat its output as an API.

## Three output formats

| `--output-format` | You get | Use for |
|---|---|---|
| `text` (default) | The final answer only | Humans, quick shell use |
| `json` | One object describing the whole run | Scripts that need the answer **and** its status |
| `stream-json` | One JSON event per line as the run happens (needs `--verbose`) | Progress, long runs, gates (next topic) |

## The run object

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "result": "line 3: divides by zero when items is empty",
  "session_id": "6c1e...",
  "num_turns": 2,
  "duration_ms": 8123,
  "total_cost_usd": 0.0123,
  "usage": { "input_tokens": 5210, "output_tokens": 96, "cache_read_input_tokens": 4100 },
  "permission_denials": [],
  "structured_output": null
}
```

| Field | Tells you |
|---|---|
| `subtype` | `success`, or why it stopped: `error_max_turns`, `error_max_budget_usd`, `error_during_execution` |
| `is_error` | One boolean to gate on |
| `result` | The final text - **absent or null** when the run failed |
| `session_id` | Resume it (`--resume`) or find its transcript |
| `num_turns`, `total_cost_usd`, `usage` | What it cost |
| `permission_denials` | Every tool call that was refused - a script that "did nothing" usually shows why here |

## jq recipes

```bash
jq -r .result run.json                                  # the answer
jq -r '"\(.subtype) turns=\(.num_turns) cost=\(.total_cost_usd)"' run.json
jq -e '.is_error == false' run.json >/dev/null          # exit 1 if the run failed
jq -r '.permission_denials[].tool_name' run.json        # what was refused
```

## Commands this node introduces

`--output-format json`, the run object's fields, and `jq -e` for gating.
