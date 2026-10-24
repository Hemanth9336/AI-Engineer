---
type: lesson
title: "Top-k queries"
minutes: 5
---

A search returns the **k** most similar records - the **top-k**. Choosing k is a trade-off you'll tune at every customer.

```python
def search(store, query_vector, k=3):
    scored = [(cosine(r["embedding"], query_vector), r) for r in store]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"id": r["id"], "text": r["text"], "score": round(s, 4)} for s, r in scored[:k]]
```

## Choosing k

| k | Effect |
|---|---|
| Too small (1) | One wrong top result and the answer is lost |
| Moderate (3-5) | Usually catches the right chunk; small prompt |
| Too large (20+) | More cost and latency; the right chunk is buried among distractors, and the model may use the wrong one |

Start around 3-5, then measure with a test set (the **hit rate** - you'll compute it in the evals section).

## Always look at the scores

Print the scores, not just the texts:

```text
0.6431  a3  International shipping and customs...
0.3452  a1  Reporting a damaged parcel...
0.3340  a5  Tracking a parcel...
```

A big gap between the first and second score means a confident match. Similar low scores across the board usually mean **nothing in the store answers the question** - a useful signal for "I don't know". Some teams set a **minimum score** below which results are discarded, but the right threshold depends on the embedding model and must be checked on real queries.

## Debug retrieval separately from generation

When an answer is wrong, first check what was retrieved. If the right chunk wasn't in the top-k, no prompt will fix it - the problem is retrieval. If it was there and the answer is still wrong, the problem is the prompt or the model. Keeping a search script you can run on its own makes this split a 10-second job.
