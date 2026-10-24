---
type: lesson
title: "Stopping conditions and runaway loops"
minutes: 5
---

An agent loop ends when the model stops calling tools. Usually it does. Sometimes it doesn't:

- A tool keeps returning an error and the model keeps retrying it.
- Two tools disagree and the model ping-pongs between them.
- A vague task ("find everything about this customer") has no natural end.
- A prompt injection in a retrieved document tells the model to keep going.

Without a limit, each of these burns tokens, hammers the customer's APIs, and leaves the user waiting - possibly for minutes. In production this is a real incident class: the "runaway agent" bill.

## Guards every agent needs

| Guard | Example |
|---|---|
| **Max steps** | At most 6 model calls per user turn |
| **Max tool calls per tool** | `create_ticket` at most once per turn |
| **Time budget** | Stop after 30 seconds |
| **Token or cost budget** | Stop after 20,000 tokens for this request |
| **Repeat detection** | Same tool, same arguments, three times in a row -> stop |

Start with **max steps**: it's one line and catches nearly every runaway.

```python
for step in range(max_steps):
    reply = ask(messages)
    if not reply["tool_calls"]:
        return reply["content"]
    ...
return f"Stopped after {max_steps} steps without an answer."
```

## What to do when the guard fires

- **Return a clear, fixed message** - the user isn't left hanging, and code can detect it.
- **Log it with the trace** - every stop is a bug report: a bad tool, a bad prompt, or an unusual question.
- **Hand off** when a human is available - "I've passed this to an agent who'll get back to you."

## Choosing the number

Look at your traces: if normal questions take 1-3 steps, a limit of 6-8 leaves headroom without allowing a runaway. Revisit it as you add tools.
