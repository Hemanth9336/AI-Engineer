---
type: lesson
title: "Everything competes for the window"
minutes: 6
---

Every model call carries a bundle of parts, and they all draw from the same budget: the context window, and your bill.

```text
| system prompt | tool definitions | history (user, assistant, tool, ...)  || answer |
     fixed           fixed               grows every step
```

| Part | Who controls it | How it grows |
|---|---|---|
| System prompt | You, at design time | Fixed - but paid on every step |
| Tool definitions | You, at design time | Fixed per tool set - also paid on every step |
| User messages | The user | Usually small |
| Assistant messages | The model | Small: reasoning text and tool calls |
| Tool results | Your tools, shaped by you | **The big one**: files, logs, listings, API dumps |

In most agent traces, tool results are 60-90% of the prompt by step 5. That's why the most effective budget work happens in **tool design** (topic 13) - but you still need numbers.

## Measure the parts, don't guess

You can't budget what you haven't measured. Use the authoritative count - the API's `usage.prompt_tokens` - and measure by difference, with `max_tokens=1` so each measurement costs almost nothing:

```python
base         = tokens([hi])                         # just a tiny user message
with_system  = tokens([system, hi])
with_tools   = tokens([system, hi], tools=SCHEMAS)
full         = tokens([system] + history, tools=SCHEMAS)

system_part  = with_system - base
tools_part   = with_tools - with_system
history_part = full - with_tools
```

The differences are approximate (message formatting adds a few tokens here and there), but they're accurate enough to see which part is eating the window.

## What the numbers usually show

```text
system   ~ 310 tokens
tools    ~ 290 tokens
history  ~ 4,900 tokens   <- one log file did this
```

Once you see that, the fix is obvious - and it's almost never "a bigger model". It's a budget for each part, enforced by the harness. That's the next lesson.
