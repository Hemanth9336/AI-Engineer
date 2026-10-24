---
type: lesson
title: "Context window limits"
minutes: 5
---

The **context window** is the maximum number of tokens a model can handle in one request - the prompt *and* the answer together.

```text
context window (e.g. 128,000 tokens)
| system prompt | documents | conversation history | question || answer (max_tokens) |
|<------------------- prompt tokens ----------------------->||<-- output tokens -->|
```

Modern models have large windows - 128,000 tokens or more is common. That sounds like plenty until you meet a customer: a 300-page policy manual, a year of ticket history, or a long chat conversation fills it quickly.

## What happens at the limit

It depends on the system, and that difference matters:

| Behaviour | Where you see it | Danger |
|---|---|---|
| **Error** - the request is rejected (HTTP 400, "context window exceeded") | Most hosted APIs and gateways | Visible, easy to handle |
| **Silent truncation** - the start or middle of the prompt is dropped | Some local runtimes, some frameworks | Answers quietly get worse - instructions or documents vanish |

An error is the friendly case. Your code must handle it: catch it, then shrink the prompt (fewer documents, shorter history, a summary) and retry.

## Bigger is not free

Even within the limit, a huge prompt:

- **costs more** - you pay for every input token, on every request;
- **is slower** - the model must process all of it before the first output token;
- **can be less accurate** - models are better at using information near the start and end of a long prompt than information buried in the middle.

That's why RAG sends a few relevant chunks instead of the whole manual.

## Your lab's tiny window

To hit the limit cheaply, your lab has **`lab-tiny`**: the same model as `lab-mini`, but the gateway allows only **2,048 input tokens**. Anything bigger is rejected with an error before it reaches the provider - just like a real context-window error, at almost no cost.
