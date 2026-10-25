---
type: lesson
title: "Observability from files"
minutes: 19
---

You can't manage what you can't see. Most agent observability doesn't need a platform, just one rule. **Every run leaves an envelope file and one line in a log**, written by a wrapper, so no script can forget.

## The wrapper

```bash
./run.sh summarize -- -p "Summarize CHANGES.md" --tools Read
```

`run.sh FLOW -- CLAUDE_ARGS...` does five things:

1. Runs `claude "${@}" --output-format json` and saves the raw envelope as `metrics/envelopes/<flow>-<timestamp>-<n>.json`.
2. Appends one row to `metrics/runs.jsonl`:

   ```json
   {"ts": "2026-10-25T07:30:02Z", "flow": "summarize", "session_id": "4c1d...", "exit_code": 0, "subtype": "success",
    "is_error": false, "cost_usd": 0.0071, "duration_ms": 2380, "num_turns": 1, "input_tokens": 1385,
    "output_tokens": 54, "cache_read_tokens": 0, "models": ["claude-sonnet-..."]}
   ```

3. Prints `.result` to stdout, so callers still get the answer.
4. Exits with `claude`'s exit code, so failures still fail.
5. Records **unreadable output** too, as `subtype: "unparsable"`. A crash that leaves no row is invisible.

## Why JSON Lines

- **Appending is atomic enough** for one writer per line. You never rewrite the file.
- `grep`, `jq`, `tail -f` and `wc -l` all work directly on it.
- Each line is self-contained, so a truncated last line costs one run, not the file.
- Moving to a real backend later is a matter of shipping the file (topic 068 covers native export).

## Questions the log answers

```bash
jq -s 'group_by(.flow) | map({flow: .[0].flow, runs: length, cost: (map(.cost_usd) | add)}) | sort_by(-.cost)' metrics/runs.jsonl
jq -c 'select(.is_error)' metrics/runs.jsonl                     # every failed run, with its session_id
jq -s 'map(.duration_ms) | sort | .[(length * 0.95 | floor)]' metrics/runs.jsonl    # p95 latency
```

The `session_id` in each row is the link to the full transcript under `~/.claude/projects/`. Aggregate numbers tell you *which* flow to look at. The transcript tells you *why*.

## Commands this node introduces

`--output-format json` in a wrapper, `metrics/runs.jsonl`, `jq -s 'group_by(...)'`, `select(.is_error)`, and exit-code passthrough.
