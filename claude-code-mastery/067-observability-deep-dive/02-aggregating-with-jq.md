---
type: lesson
title: "Aggregating with jq"
minutes: 14
---

## Slurp

By default, `jq` runs its filter **once per input value**. `jq '.total_cost_usd' runs/*/*.json` prints one number per file. With `-s` (`--slurp`), jq reads *all* inputs into one array first and runs the filter once on that array. Totals and grouping need slurp.

```bash
jq '.total_cost_usd' runs/*/*.json                 # 0.0071  0.0071  0.0081   (three outputs)
jq -s 'map(.total_cost_usd) | add' runs/*/*.json   # 0.0223                    (one output)
```

## Knowing which file a value came from

`input_filename` gives the current file's path. It's only available while jq is reading inputs, so tag each file *before* slurping:

```bash
jq -c '{task: (input_filename | split("/") | .[-2]), cost: .total_cost_usd}' runs/*/*.json \
  | jq -s 'group_by(.task) | map({task: .[0].task, runs: length, cost: (map(.cost) | add)})'
```

## The building blocks

| Filter | Does |
|---|---|
| `group_by(.task)` | Sorts and splits an array into arrays of equal `.task` |
| `map(f)`, `add`, `length` | Transform each element, sum an array, count |
| `(map(.x) | add) / length` | Average |
| `.x // 0` | Default for a missing or null field |
| `@csv`, `@tsv` | Format an array as one CSV or TSV line (strings quoted) |
| `-r` | Raw output, so CSV lines aren't wrapped in JSON quotes |

```bash
jq -r '["task","runs","cost_usd"], (.[] | [.task, .runs, .cost]) | @csv'
```

## Skipping corrupt files

jq stops at the first unparsable input. Validate each file first, `jq -e type f > /dev/null 2>&1`, and pass only the good ones on:

```bash
good=()
for f in runs/*/*.json; do
  if jq -e 'type == "object" and .type == "result"' "$f" > /dev/null 2>&1; then good+=("$f"); else echo "skipped: $f" >&2; fi
done
```

## Commands this node introduces

`jq -s` (`--slurp`), `input_filename`, `group_by`, `map`, `add`, `length`, `//`, `@csv`, and `jq -r`.
