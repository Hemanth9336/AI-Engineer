---
type: lesson
title: "Querying the store, worked through"
minutes: 7
---

Now the other half: given a question, return the closest chunks.

```python
import json
import math
import sqlite3
import sys

from openai import OpenAI

client = OpenAI()


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def search(question, k=3):
    qv = client.embeddings.create(model="lab-embed", input=question).data[0].embedding
    db = sqlite3.connect("store.db")
    rows = db.execute("SELECT id, text, embedding FROM chunks").fetchall()
    scored = [(cosine(qv, json.loads(emb)), cid, text) for cid, text, emb in rows]
    return sorted(scored, reverse=True)[:k]


for score, cid, text in search(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3):
    print(f"{score:.4f}  {cid}  {text[:60].replace(chr(10), ' ')}")
```

```bash
python query_store.py "When are core hours?"
```

```text
0.6058  handbook-000  # Northwind Employee Handbook  ## Working hours Core hours
0.3457  handbook-001  head for anything longer than three days. Unused days can b
0.2152  handbook-004  y Give four weeks of notice in writing to your manager and
```

## Notice what's embedded

Only the **question** is embedded at query time - one small call. The chunk vectors come from the database. That's the payoff of indexing once.

## This is a "flat" search

It compares the query against **every** stored vector. For thousands of chunks it's instant. For millions, it's too slow - real vector databases build an index (like **HNSW**, a graph of neighbours) that finds the nearest vectors without checking them all. Same answer, much faster, at the cost of being *approximately* rather than exactly nearest. You get that for free with Chroma next topic.

## Printing a preview

`text[:60].replace(chr(10), " ")` shows the first 60 characters with newlines turned into spaces, so each hit stays on one line. Your program should still keep the **full** text - that's what goes into the prompt.
