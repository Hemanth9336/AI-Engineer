---
type: lesson
title: "The JSON envelope"
minutes: 14
---

Plain `claude -p` prints only the final text. Add `--output-format json` and you get one JSON object describing the whole run - the **envelope**:

```bash
claude -p "How many lines are in audit.py?" --output-format json > run.json
jq . run.json
```

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 8412,
  "duration_api_ms": 6120,
  "num_turns": 2,
  "result": "audit.py has 14 lines.",
  "stop_reason": "end_turn",
  "session_id": "79ac92a4-73b8-45ea-8b7b-82e4e14a063c",
  "total_cost_usd": 0.0243,
  "usage": { "input_tokens": 4781, "output_tokens": 15, "cache_read_input_tokens": 0 },
  "modelUsage": { "claude-haiku-...": { "costUSD": 0.0243 } },
  "permission_denials": [],
  "terminal_reason": "completed"
}
```

| Field | Use it for |
|---|---|
| `result` | The final answer text |
| `subtype`, `is_error` | Did it succeed? `success`, or `error_max_turns`, `error_during_execution`, `error_max_budget_usd` |
| `num_turns` | How many times the loop went around |
| `duration_ms`, `duration_api_ms` | Wall time, and time spent waiting on the model |
| `total_cost_usd`, `usage`, `modelUsage` | Estimated spend and tokens, per model |
| `permission_denials` | Tool calls that were refused |
| `session_id` | The key to the full transcript on disk |

The envelope is a summary. It does not list the tool calls - those live in the session transcript. The `session_id` connects the two:

```bash
sid=$(jq -r .session_id run.json)
ls ~/.claude/projects/*/"$sid".jsonl
```

Envelope plus transcript is the complete record of a run: what it cost, how it ended, and every step in between.

## Commands this node introduces

`--output-format json` returns the envelope; `jq -r .field` pulls one value out of it.
