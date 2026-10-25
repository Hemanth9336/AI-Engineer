---
type: lesson
title: "Golden tasks with checkable outcomes"
minutes: 8
---

A **golden task** is a test case for an agent: a prompt, plus checks that decide - by code, with no judgment - whether the run passed. A set of them is your eval suite, and it's the most valuable thing in a harness repo after the harness itself.

## The shape of a golden task

```json
{"id": "write-note",
 "prompt": "Create notes/oncall.md with the line 'Billing on-call: Priya'.",
 "expect": [{"file_contains": {"path": "notes/oncall.md", "text": "Billing on-call: Priya"}}]}
```

- **id** - stable and readable, so results can be compared across runs.
- **prompt** - exactly what a user would type. Real phrasing, including vague and messy phrasing.
- **expect** - a list of checks; the task passes only if **all** pass.

## The check vocabulary

Keep it small and objective:

| Check | Kind | Example |
|---|---|---|
| `answer_contains` | outcome | `"8081"` |
| `file_contains` | outcome | `{"path": "notes/oncall.md", "text": "Priya"}` |
| `file_unchanged` | outcome / safety | `"README.md"` |
| `file_absent` | outcome | `"tmp/cache.txt"` |
| `tool_called` | step | `"read_file"` - it looked instead of guessing |
| `tool_not_called` | step / safety | `"delete_file"` |
| `max_tool_calls` | efficiency | `2` |

## What a first suite covers

| Category | Why | Example |
|---|---|---|
| **Lookups** | The everyday job | Ports, owners |
| **Changes** | Writes must land correctly | Create a note file |
| **Must-never** | Safety rules, as tests | "Clean up the workspace" must not delete anything |
| **Efficiency** | Catch loops and wandering | List a folder in at most 2 tool calls |
| **Ambiguity** | Real users are vague | "Fix the billing config" - should it ask? |

Start with 6-20 tasks. Grow the suite every time something goes wrong in production: **every bug becomes a golden task**, so it can't come back silently.

## Checks that can't pass by accident

A check is only useful if it can fail. Watch out for:

- `file_contains` on text the file **already** had before the run.
- `answer_contains` with a string that's in the prompt - the model can just echo it.
- Checks that are too loose: `answer_contains: "port"` passes on "I don't know the port".
