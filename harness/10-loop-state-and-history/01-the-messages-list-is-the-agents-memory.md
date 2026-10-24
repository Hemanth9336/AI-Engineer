---
type: lesson
title: "The messages list is the agent's memory"
minutes: 6
---

Your agent has no memory. The model forgets everything between calls (topic 02). What looks like memory is one Python list - `messages` - that your loop builds up and re-sends on every call.

```python
messages = [
    {"role": "system", "content": SYSTEM},                       # who the agent is, the rules
    {"role": "user", "content": "Which port does billing use?"},  # the task
    # ... every step appends here ...
]
```

Whatever is in that list, the agent "knows". Whatever isn't, it doesn't - no matter how many steps ago it saw it.

## Three consequences

1. **The list is state, so treat it like state.** It's the single most important variable in your harness. Log it, dump it when something goes wrong, and never mutate it carelessly.
2. **It only grows - until you shrink it.** Every step adds at least one assistant message and one tool result. By step 20 the list can be tens of thousands of tokens. Shrinking it safely is topics 17 and 18.
3. **It must stay valid.** The API checks its structure: every tool result must answer a tool call that came just before it. One bad append and the next request fails - or worse, the model sees a result attached to the wrong question.

## Plain dicts, not SDK objects

The SDK returns message **objects**. Appending them works for the next request, but you can't `json.dumps` them, save them, or reload them after a crash. Convert to plain dicts as you append:

```python
def as_dict(msg):
    d = {"role": "assistant", "content": msg.content}
    if msg.tool_calls:
        d["tool_calls"] = [{"id": c.id, "type": "function",
                            "function": {"name": c.function.name, "arguments": c.function.arguments}}
                           for c in msg.tool_calls]
    return d
```

Now the whole memory is JSON: you can print it, diff two runs, resume from a file (topic 19), or replay it into a new model (topic 31).

## Watch it grow

A one-line log per step - number of messages and total size - shows the growth at a glance:

```text
step 1: 2 messages, 410 chars
step 2: 4 messages, 655 chars
step 3: 6 messages, 1,904 chars     <- a file landed in the history
```

That line is what you'll add in the next task.
