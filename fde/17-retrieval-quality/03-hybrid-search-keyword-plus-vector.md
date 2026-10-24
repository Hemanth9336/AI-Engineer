---
type: lesson
title: "Hybrid search: keyword plus vector"
minutes: 5
---

**Hybrid search** runs two searches and merges them: vector search for meaning, keyword search for exact terms. Each covers the other's blind spot.

## Keyword search

Production systems use **BM25** (in Elasticsearch, OpenSearch, PostgreSQL full-text search and most vector databases), which scores documents by how often the query's words appear, weighted so rare words count more. For learning, a simplified version shows the idea:

```python
STOP = {"a", "an", "and", "can", "do", "is", "the", "we", "what", ...}

def tokens(s):
    return set(re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", s.lower()))

def keyword_score(query, doc):
    return len((tokens(query) - STOP) & tokens(doc))
```

"Can we get DDP?" becomes the terms `{get, ddp}`, and only the customs article contains `ddp`.

## Merging: reciprocal rank fusion

Vector scores (0.0-1.0) and keyword scores (0, 1, 2...) aren't comparable, so instead of adding scores you combine **ranks**. **Reciprocal rank fusion (RRF)**:

```text
score(doc) = 1 / (60 + vector_rank) + 1 / (60 + keyword_rank)
```

Ranks start at 1. Documents with no keyword match get no keyword term. The constant 60 is the standard choice; it stops the very top rank from dominating.

```text
Can we get DDP?    vector ranks: a4=1  a2=2  a3=3 ...    keyword ranks: a3=1
a3: 1/63 + 1/61 = 0.0323     a4: 1/61 = 0.0164     a2: 1/62 = 0.0161
-> hybrid order: a3, a4, a2
```

The customs article wins because it does reasonably on meaning **and** is the only exact match.

## Why RRF is popular

- No score calibration needed - only ranks.
- Robust: a document that's strong in either list rises.
- Easy to explain to a customer: "it's in the top of both lists".

Many vector databases now offer hybrid search built in. Know what it does underneath, so you can tell when it helps and debug it when it doesn't.
