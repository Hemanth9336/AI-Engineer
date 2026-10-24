---
type: lesson
title: "Runaway loops and max steps"
minutes: 5
---

A **runaway loop** is an agent that never stops: it keeps calling tools, and each call costs more than the last because the history keeps growing.

## How it happens

| Pattern | What it looks like in the trace |
|---|---|
| **Repeating** | `list_dir(".")`, `list_dir(".")`, `list_dir(".")` - the same call, same result |
| **Oscillating** | reads file A, then B, then A, then B... |
| **Retrying a failure** | calls a broken tool again and again, hoping for a different result |
| **Scope creep** | finishes the task, then keeps "improving" things nobody asked for |
| **Ignoring done** | never calls `finish` |

None of these need a bad model. A vague tool description, an unclear goal, or an error message that doesn't say what to do next is enough.

## The cost of one runaway

Say each step adds 1,500 tokens of history. Step *n* sends about 1,500 x *n* prompt tokens, so 200 steps send about **30 million** tokens - for one task. Multiply by a few hundred users and a weekend.

## The fix: a hard step limit

The harness, not the model, decides the maximum number of steps:

```python
def run(question, max_steps=8):
    ...
    for step in range(1, max_steps + 1):
        msg = call_model(messages)
        ...
    return "stopped: reached max steps (8)"
```

Rules for a good limit:

- **Always have one.** Every loop, every agent, every subagent.
- **Size it from data.** Look at traces of successful runs: if 95% finish in 6 steps, a limit of 12-15 is generous.
- **Fail loudly.** Return a clear "stopped" result and a non-zero exit status, so callers and monitors can tell a limit hit from a real answer.
- **Combine it** with a token or cost budget (topic 32) - a few huge steps can be as expensive as many small ones.

## Bonus: repeat detection

A cheap extra guard: if the model makes the **same call with the same arguments** three times in a row, stop or tell it so. It catches the most common runaway long before the step limit does.

In the task you'll build a runaway on purpose with labmock - a script whose last step repeats forever - and watch your cap stop it.
