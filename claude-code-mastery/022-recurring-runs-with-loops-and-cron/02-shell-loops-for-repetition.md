---
type: lesson
title: "Shell loops for repetition"
minutes: 10
---

The simplest recurrence is a loop in bash.

## Repeat N times

```bash
for i in 1 2 3; do
  claude -p "$(cat prompts/flaky.md)" --output-format json > "runs/flaky-$i.json"
done
```

Useful for **flakiness checks** - run the same diagnosis three times and compare - or for processing a list:

```bash
while read -r svc; do
  claude -p "Summarize open TODOs in services/$svc" --output-format json > "reports/$svc.json"
done < services.txt
```

## Repeat until a condition

```bash
for attempt in 1 2 3 4 5; do
  claude -p "Run the tests; fix one failing test if any" --permission-mode acceptEdits \
    --allowedTools "Bash(python3 -m unittest *)" --max-turns 15 --output-format json > run.json
  python3 -m unittest -q && break
  sleep $((attempt * 30))
done
```

## Rules for loops

- **Always bound them** - a counter, `--max-turns`, and a timeout (`timeout 600 claude -p ...` on Linux).
- **Check the result each iteration**, not just the exit code: `jq -e '.subtype == "success"' run.json`.
- **Back off** between attempts; do not hammer an API in a tight loop.
- **Write each iteration's envelope to its own file**, so you can see what changed between attempts.
- **Stop on denials**: a non-empty `permission_denials` means the loop lacks a permission - repeating will not help.

## Commands this node introduces

`jq -e` exits non-zero when the expression is false or null, which turns an envelope check into an `if` or `&&` condition.
