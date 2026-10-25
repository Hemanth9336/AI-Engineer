---
type: lesson
title: "Reusable prompt files"
minutes: 14
---

Before you build a skill, there is a simpler step: **save the prompt in a file**. A prompt file under version control is reviewable, diffable, and identical every time - unlike the version you retype from memory.

```text
prompts/
└── review.md
```

```bash
claude -p "$(cat prompts/review.md)
File: src/billing.py" --output-format json > reviews/billing.json
```

## What makes a prompt reusable

- **A fixed output format.** "Reply with exactly four lines, `R<n>: PASS` or `R<n>: FAIL - <line> <reason>`" turns the answer into something a script or a reviewer can compare across files and across weeks.
- **Stable ids for every check.** `R1`...`R4` let you track "R3 failures went from 6 to 0".
- **A parameter slot.** The prompt names *what* to check; the file name is appended per run.
- **No conversational filler.** It is a specification, not a chat message.

## When to promote it to a skill or command

| Signal | Next step |
|---|---|
| You run it by hand with `$(cat ...)` | Fine - a prompt file is enough |
| Teammates should type it as `/review` | A project command or skill (topics 014-015) |
| Claude should apply it on its own when relevant | A skill with a good description |
| It needs scripts or reference files | A skill folder |

## Commands this node introduces

`claude -p "$(cat prompts/review.md)"` runs a saved prompt; `jq -r .result` extracts the answer for a report.
