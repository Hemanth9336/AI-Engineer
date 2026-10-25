---
type: lesson
title: "Constrained output, bounded runs, and failing closed"
minutes: 12
---

## Ask for a shape, get a shape

```bash
claude -p "Run the tests and give a verdict" --output-format json \
  --json-schema '{"type":"object","properties":{"verdict":{"type":"string","enum":["pass","fail"]},"failures":{"type":"integer","minimum":0},"summary":{"type":"string"}},"required":["verdict","failures","summary"]}'
```

Claude Code gives the model a tool to return the answer in that shape and validates it. The validated object arrives in **`structured_output`** (in the `result` event or the json object); `result` holds the same thing as text.

- An invalid schema stops claude before it starts: `Error: --json-schema is not a valid JSON Schema`.
- `format` (like `"email"`) is accepted but **not** enforced.
- If the model never returns valid structured output - it declined, or ran out of turns - the run can still say `success` with exit code `0` and **no `structured_output`**.

## Fail closed

A gate decides "ship" or "stop". Anything it does not understand must mean **stop**:

| Situation | Gate |
|---|---|
| No `result` event (stream cut off) | Stop |
| A line that is not JSON | Stop |
| `is_error` true or `subtype` not `success` | Stop |
| `structured_output` missing | Stop |
| Values that contradict each other (`verdict: pass` with `failures: 2`) | Stop |
| Everything checks out and the verdict is `pass` | Go |

Check the schema yourself too - the gate should not trust a field just because it exists.

## Bound it

`--max-turns`, `--max-budget-usd`, and a wall-clock limit in the CI job itself. A gate that can hang is a gate someone will disable.

## Commands this node introduces

`--json-schema` and the `structured_output` field.
