---
type: lesson
title: "Automations that take input"
minutes: 19
---

The flow in topic 061 took a folder and a date. Most useful automations take an **input file**, such as a changelog, a CSV export or a ticket dump, and turn it into one artefact per input. Two things change: validating the input, and reading the agent's answer reliably.

## Validate before you spend

```bash
file=${1:?usage: blurb.sh CHANGES_FILE}
[ -s "$file" ] || { echo "not found or empty: $file" >&2; exit 2; }
name=$(basename "$file" .txt)
```

Exit **2** for bad input, the usual "you called me wrong" code. That way a caller can tell a usage error from a model failure (exit 1 or 3) without parsing messages. A missing file should never cost a model call.

## Read the envelope, not the text

`claude -p` prints plain text by default. Plain text can't tell you the run failed. An error message such as `Reached maximum number of turns` arrives on stdout just like an answer would. `--output-format json` wraps the run in an envelope:

```json
{"type": "result", "subtype": "success", "is_error": false, "result": "...the answer...",
 "session_id": "4c1d...", "num_turns": 1, "duration_ms": 2380, "total_cost_usd": 0.0071,
 "usage": {"input_tokens": 1385, "output_tokens": 54, "cache_read_input_tokens": 0}}
```

```bash
claude -p "$prompt" --tools "" --output-format json < "$file" > "work/$name.envelope.json" || rc=$?
jq -e '.is_error == false and .subtype == "success"' "work/$name.envelope.json" > /dev/null 2>&1 \
  || { echo "agent step failed: $(jq -r '.errors // .result // "unreadable envelope"' "work/$name.envelope.json" 2>/dev/null)" >&2; exit 3; }
jq -r '.result' "work/$name.envelope.json" > "out/$name.md"
```

| You need | Read |
|---|---|
| Did it work? | `.is_error`, `.subtype`, plus the exit code |
| The answer | `.result`, or `.structured_output` with `--json-schema` (topic 053) |
| Cost and speed for your logs | `.total_cost_usd`, `.duration_ms`, `.num_turns`, `.usage` |
| Where to look when it's wrong | `.session_id`, which identifies the transcript under `~/.claude/projects/` |

Keep the raw envelope next to the output. When someone asks "why does the 2.4.0 blurb say that?", the session id and cost are one `jq` away.

## One input, one set of outputs

Name outputs after the input (`out/2.4.0.md`, `out/2.4.0.meta.json`). Then re-running one input replaces exactly its own files, a batch is just a loop, and nothing collides:

```bash
for f in changes/*.txt; do ./blurb.sh "$f" || echo "FAILED $f" >&2; done
```

## Commands this node introduces

`${1:?usage}`, exit code 2 for bad input, `--output-format json`, `.is_error`, `.subtype`, `.result`, `jq -e`, and per-input output naming.
