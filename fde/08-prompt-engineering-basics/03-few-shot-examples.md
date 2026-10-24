---
type: lesson
title: "Few-shot examples"
minutes: 5
---

Some things are easier to **show** than describe. A **few-shot** prompt includes a handful of worked examples before the real input; the model copies the pattern.

## As chat messages

The cleanest way with a chat API is fake turns: each example is a user message followed by the assistant reply you want.

```python
messages = [
    {"role": "system", "content": "Classify the ticket. Reply with one label: damaged, late, address, billing, other."},
    {"role": "user", "content": "The box was crushed and two jars broke."},
    {"role": "assistant", "content": "damaged"},
    {"role": "user", "content": "Tracking says delivered yesterday but it still hasn't arrived... wait, it says out for delivery since Monday."},
    {"role": "assistant", "content": "late"},
    {"role": "user", "content": "I was charged twice for the same shipment."},
    {"role": "assistant", "content": "billing"},
    {"role": "user", "content": ticket_text},      # the real input
]
```

The model sees that "assistant" always answers with one bare lowercase label - no sentence, no explanation - and does the same.

## Choosing good examples

- **Cover each label at least once**, or the model will under-use the missing ones.
- **Include a hard case**: an ambiguous ticket with the label you've decided is right. Examples are where you encode the customer's judgement.
- **Use real (anonymised) inputs**, not tidy invented ones. Real tickets are messy, and the model should see that.
- **Keep them short.** Every example is sent on every request - you pay for them each time.
- **Vary the order** of labels so the model doesn't learn "the answer is usually the last one shown".

## When to use few-shot

| Good fit | Better alternative |
|---|---|
| A specific output style or label set | - |
| Customer-specific judgement calls | - |
| Strict machine-readable output | JSON mode or tool calling (next lessons) |
| Teaching facts | Put the facts in the prompt (RAG) |
