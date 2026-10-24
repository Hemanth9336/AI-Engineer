---
type: lesson
title: "Perceived vs real latency"
minutes: 5
---

A support answer that takes 6 seconds feels broken. The same answer, appearing word by word after 400 ms, feels fast - even though it finishes at exactly the same moment. Users judge speed by **when something starts happening**, not when it's done.

## Two numbers to track

| Metric | Meaning | Typical target for chat |
|---|---|---|
| **Time to first token (TTFT)** | From sending the request to the first visible text | Under 1 second |
| **Total latency** | Until the last token | Depends on answer length; a few seconds is normal |

## Where the time goes in a RAG request

```text
embed the question         ~50 ms
vector search              ~20 ms
rerank (if any)           ~300 ms
model: time to first token ~400 ms
model: generate 200 tokens ~2-4 s
```

Generation dominates, and it scales with **output length**. That gives you the main levers:

- **Stream** the output so text appears as it's generated.
- **Ask for shorter answers** - fewer output tokens is the biggest real speed-up.
- **Use a smaller model** where quality allows (topic 33) - faster per token.
- **Do retrieval work in parallel**, and skip steps (reranking) that don't pay for themselves.
- **Show progress** for multi-step agents: "Checking your order..." while tools run.

## Streaming in the SDK

```python
stream = client.chat.completions.create(model="lab-fast", messages=messages, stream=True)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

Each chunk carries a small **delta** - a few characters or a word. `flush=True` matters: without it, Python buffers the output and the user sees nothing until the end.

## Streaming has costs

You can't run an output filter (topic 31) on text the user has already seen. Common patterns: filter per sentence as it streams, or stream only after a quick check of the first part - or don't stream answers that must be checked as a whole, such as JSON.
