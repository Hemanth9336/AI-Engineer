---
type: lesson
title: "The result goes into context, shape it"
minutes: 6
---

Whatever a tool returns goes **straight into the model's context** - and stays there, re-sent on every later step. A tool result is not just data for the model. It is a chunk of the model's world, paid for again and again.

## The 400 KB log

```python
def read_log(service):
    return open(f"logs/{service}.log").read()     # 5,000 lines, ~400 KB
```

One call adds roughly **100,000 tokens** to the history. On a 128k-token model, the agent has almost no room left. On every later step you pay for those tokens again. And the model has to find the 52 ERROR lines that matter among 4,948 that don't - where models are weakest, in the middle of a long context.

## Shape results for the reader

The reader is a model with limited attention. Give it what it needs for the next decision, and **tell it what it isn't seeing**:

```text
52 matching lines out of 5000; showing 20
2026-03-14T00:00:00Z ERROR search: upstream timeout after 2000ms request_id=r00000 trace=frame;frame;frame;frame;...
2026-03-14T00:01:37Z ERROR search: upstream timeout after 2000ms request_id=r00097
...
Narrow the search with contains= or raise limit (max 50).
```

| Technique | Why |
|---|---|
| **Filter at the source** (`level=`, `contains=`) | Send the 52 lines that matter, not 5,000 |
| **Cap the count** (`limit=20`, max 50) | A bound you choose, not one the data chooses |
| **Cut long lines** (first 200 characters) | One stack trace shouldn't eat the budget |
| **Say what was cut** ("showing 20 of 52") | The model knows there's more, and can ask |
| **Say how to get more** ("narrow with contains=") | The next call is obvious |

## Structured or plain?

Both work. Short, labelled plain text is usually cheaper in tokens than verbose JSON with repeated keys. Use JSON when the model must pass values on exactly (ids, paths); use text for things to read.

## The 10x rule of thumb

If a typical result is ten times larger than what the model needs to decide its next step, the tool is doing the harness's job badly. Rewrite the tool before reaching for a bigger context window.
