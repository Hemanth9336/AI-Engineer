---
type: lesson
title: "Caching repeated work"
minutes: 5
---

Support traffic is repetitive. On a busy morning hundreds of people ask "where is my parcel?" and "when are you open?". If every one of those runs retrieval and a model call, you're paying again and again for the same answer.

## What to cache

| Layer | Key | Saves |
|---|---|---|
| **Embeddings of documents** | Chunk text hash | Re-embedding unchanged chunks on every re-index (topic 24) |
| **Query embeddings** | Normalised query | One embedding call per repeat |
| **Full responses** | Model + system prompt + normalised question (+ sources) | The whole model call |
| **Provider prompt caching** | Automatic, for long identical prompt prefixes | Part of the input price on every call |

## The cache key is the design

Everything that can change the answer must be in the key:

```python
key = sha256(f"{model}\n{system_prompt}\n{normalise(question)}")
```

- **Model and prompt** - change either and old answers must not be served.
- **Normalised question** - lower-case, collapse whitespace, so "Where  is my PARCEL?" hits the same entry.
- **Sources or index version** for RAG - when documents change, so must the answers.
- **User or tenant** if answers depend on permissions (topic 19) - never serve one user's cached answer to another.

## When not to cache

Answers that depend on live data ("where is **order MER-55120**?" -> a tool call), personal data, or anything time-sensitive. Cache those with a short expiry or not at all.

## Measure the savings

Count hits, misses and the tokens each hit saved. A 30% hit rate on FAQ traffic is common - often the cheapest cost win in the whole project.
