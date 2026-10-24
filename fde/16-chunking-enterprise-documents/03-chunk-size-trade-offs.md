---
type: lesson
title: "Chunk size trade-offs"
minutes: 5
---

When documents have no useful headings - a long email thread, a transcript, a flattened PDF - you fall back to fixed-size chunks. Then size becomes a real choice.

| | Small chunks (~50-100 words) | Large chunks (~300-800 words) |
|---|---|---|
| Retrieval precision | High - each vector is about one thing | Lower - meaning gets averaged |
| Context per chunk | Little - a rule may lose its conditions | Plenty - the full rule and its exceptions |
| Chunks per answer | Need more (higher k) | Fewer |
| Tokens sent | Fewer per chunk | More per chunk |
| Typical failure | Fact split across chunks; out-of-context snippets | Right section retrieved, but the fact is buried and the score is diluted |

## Overlap

Fixed-size chunking often uses **overlap**: each chunk repeats the last 10-20% of the previous one, so a sentence cut at a boundary appears whole in at least one chunk. It costs some extra storage and tokens.

## There's no universal best size

It depends on the documents, the questions and the embedding model. A size that's perfect for short FAQ answers is wrong for contracts. The FDE approach:

1. Pick two or three candidate sizes.
2. Run your real questions against each.
3. Measure which one gets the right chunk into the top-k most often.

Common starting points: sections where structure exists; otherwise 200-400 tokens with 10-15% overlap.

## Small-to-big

A popular pattern combines both: **search over small chunks** for precision, then **send the larger surrounding section** to the model for context. The small chunk stores a pointer to its parent section.

In the task you'll compare two sizes on the same question and see the difference in what gets retrieved.
