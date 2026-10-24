---
type: lesson
title: "Retrieval hit rate"
minutes: 5
---

When a RAG answer is wrong, there are two very different causes:

1. **Retrieval failed** - the right document never reached the model.
2. **Generation failed** - the right document was there, and the model still got it wrong.

They have different fixes (chunking, hybrid search and reranking vs prompts and models), so measure them separately. Retrieval is the easier one, because you don't need a judge: your golden set already says which document holds each answer.

## Hit rate at k

> **hit@k** = the fraction of questions whose source document appears in the top k retrieved results.

| Metric | Question it answers |
|---|---|
| **hit@1** | How often is the best match the right one? |
| **hit@3** | If we send three chunks, how often is the right one among them? |
| **misses** | Which questions never got their source in the top k? |

If you send the model three chunks, **hit@3 is the ceiling on answer quality**: a question whose source isn't retrieved can only be answered by guessing.

## Reading it

- **hit@3 high, answers still wrong** - look at the prompt and model.
- **hit@3 low** - fix retrieval first: chunk differently, add keyword search (topic 17), rerank, or rewrite queries.
- **Misses cluster on a topic** - often a vocabulary mismatch: users say "crushed", the doc says "damaged".

Because hit rate is cheap - embeddings only, no chat calls - you can run it on every chunking or embedding change in seconds.

## The source field

This is why every golden case has a `source` (topic 26). For chunked documents, store the chunk or section id, or accept any chunk from the right document.
