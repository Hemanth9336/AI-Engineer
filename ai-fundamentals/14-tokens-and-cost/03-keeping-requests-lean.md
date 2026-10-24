---
type: lesson
title: "Keeping requests lean"
minutes: 7
---

Fewer tokens means lower cost, faster replies, and often better answers. Here is where tokens hide and how to cut them.

## Trim the input

- **Send only the relevant part.** The 20 lines around an error, not the whole 50 MB log. `grep -B5 -A15 ERROR` is a prompt-engineering tool.
- **Trim history.** Sliding window or summary (topic 12).
- **Tighten the system prompt.** A 2,000-token system prompt is paid for on every single request.
- **Offer only the tools you need.** Each tool definition costs input tokens.

## Limit the output

Output tokens are the expensive ones.

- **Ask for brevity**: "at most 3 bullet points", "one line".
- **Ask for structure** instead of prose: `{"label": "bug"}` is a few tokens; a paragraph explaining the label is a hundred.
- **Set `max_tokens`** as a safety cap so a runaway reply can't cost much - but remember a cut-off reply is often useless, so it is a guard, not a way to shorten answers.

## Choose the right model

The biggest saving is often the model tier (topic 13). A small model on a lean prompt can be 100x cheaper than a frontier model on a bloated one.

## Reuse what you can

- **Prompt caching** - put the fixed part of your prompt (instructions, examples, documents) at the **start**, and the changing part at the **end**. Providers cache matching prefixes.
- **Cache answers** in your own code for identical questions.

## Measure every change

Treat tokens like any other performance metric. Before and after a change, compare `usage.prompt_tokens` and `usage.completion_tokens` - and check the answer did not get worse. Next, measure one request and price it.
