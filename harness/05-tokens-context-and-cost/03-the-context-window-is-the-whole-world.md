---
type: lesson
title: "The context window is the whole world"
minutes: 5
---

The **context window** is the maximum number of tokens a model can handle in one request - prompt and answer together. For an agent, it's more than a limit. It is **everything the agent knows** at that step.

```text
context window (e.g. 128,000 tokens)
| system prompt | tool definitions | history: steps 1..n | tool results || answer |
|<----------------------- prompt tokens -------------------------->||<-output->|
```

Nothing outside the window exists for the model: not the file it read ten steps ago (unless that result is still in the history), not the user's original request (if your code dropped it), not the rules (if they aren't in the system prompt).

## An agent fills its window fast

A chat assistant adds a few hundred tokens per turn. An agent adds **tool results**: a directory listing, a 2,000-line log, a database dump. A handful of careless tool calls can fill 128,000 tokens.

| Part | Sent | Typical size |
|---|---|---|
| System prompt | every step | 500 - 3,000 |
| Tool definitions | every step | 100 - 400 per tool |
| History | every step, growing | grows without limit |
| Tool results | every step after they arrive | 10 - 50,000 each |

## What happens at the limit

| Behaviour | Where you see it | Danger |
|---|---|---|
| **Error** - request rejected ("context window exceeded") | Most hosted APIs and gateways | Visible: the loop crashes mid-task |
| **Silent truncation** - part of the prompt is dropped | Some local runtimes and frameworks | The agent quietly loses its instructions or the user's request |

Both are harness problems. The fixes - result trimming (topic 13), budgets (topic 17), compaction (topic 18) and file memory (topic 19) - all decide **what earns a place in the window**.

## Bigger is not free

Even under the limit, a huge context costs more on **every** step, is slower to the first token, and is used less reliably - models pay most attention to the start and end, less to the middle.

## Your lab's tiny window

To hit the limit cheaply, your lab has **`lab-tiny`**: the same model as `lab-mini`, but the gateway allows only **2,048 input tokens**. Anything bigger is rejected before it reaches the provider - just like a real context-window error.
