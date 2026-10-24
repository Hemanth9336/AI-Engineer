---
type: lesson
title: "Budgeting prompt, history, and tool results"
minutes: 6
---

A **context budget** is a limit per part, enforced by the harness before every model call. It turns "the agent sometimes runs out of context on long tasks" into "the agent never sends more than N".

## A budget per part

| Part | Typical budget | Enforced by |
|---|---|---|
| System prompt | 1,000-2,000 tokens | Review: it's fixed, so check it once per change |
| Tool definitions | ~150 tokens per tool, 5-10 tools | Tool set design (topic 14) |
| Each tool result | 1,000-3,000 tokens | **Truncate** with a marker, right after the tool runs |
| History total | whatever is left, minus room for the answer | **Drop or compact** old turns before each call |

Characters are a fine proxy inside the harness: about 4 characters per token for English, fewer for code and logs. Use real token counts for setting budgets, and cheap character counts for enforcing them on every step.

## Enforcing it before every call

```python
def enforce(messages, budget):
    head = messages[:2]                     # system + the user's task: never dropped
    rest = trim_tool_results(messages[2:], budget["tool_result_chars"])
    groups = turns(rest)                    # [assistant + its tool results], ...
    dropped = 0
    while len(groups) > 1 and size(groups) > budget["history_chars"]:
        groups.pop(0)                       # oldest whole turn first
        dropped += 1
    note = [{"role": "user", "content": f"[note: {dropped} earlier steps were dropped to fit the context budget]"}] if dropped else []
    return head + note + flatten(groups)
```

The rules that keep it safe:

1. **Never drop the system prompt or the task.** They're the agent's goal and rules.
2. **Drop whole turns.** An assistant message and all its tool results go together - otherwise the history is invalid (topic 10).
3. **Never drop the most recent turn.** The model needs the result it just asked for.
4. **Leave a note.** The model should know earlier steps existed, so it doesn't redo them blindly.
5. **Mark truncation inside results**, as in topic 13: `[truncated: 38,412 more characters]`.

## Dropping is the crude version

Dropping old turns loses information. The agent may forget what it already learned and repeat work. The next topic replaces dropping with **compaction**: summarizing old turns instead of deleting them. Dropping is still the right last resort when even the summary doesn't fit.
