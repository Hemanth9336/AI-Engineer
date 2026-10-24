---
type: lesson
title: "Querying Chroma, worked through"
minutes: 7
---

Querying is one call. Pass the question **text** - Chroma embeds it with the collection's embedding function.

```python
import os

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

embed = OpenAIEmbeddingFunction(
    api_key_env_var="OPENAI_API_KEY", api_base=os.environ["OPENAI_BASE_URL"], model_name="lab-embed"
)
collection = chromadb.PersistentClient(path="db").get_collection("handbook", embedding_function=embed)

res = collection.query(query_texts=["When are core hours?"], n_results=3)
print(res["ids"])
print(res["distances"])
```

```text
[['handbook-000', 'handbook-001', 'handbook-004']]
[[0.3942, 0.6543, 0.7848]]
```

## Why lists of lists?

`query_texts` takes **several** questions at once, so every field is a list with one entry per question. For one question, take `[0]`:

```python
for cid, dist, doc, meta in zip(res["ids"][0], res["distances"][0], res["documents"][0], res["metadatas"][0]):
    print(f"{1 - dist:.4f}  {cid}  {meta['source']}  {doc[:40].replace(chr(10), ' ')}")
```

```text
0.6058  handbook-000  handbook.md  # Northwind Employee Handbook  ## Wor
0.3457  handbook-001  handbook.md  head for anything longer than three d
0.2152  handbook-004  handbook.md  y Give four weeks of notice in writin
```

Same ranking and the same scores as your SQLite store (0.6058, 0.3457, 0.2152) - because it's the same embeddings and the same cosine math. Chroma just does it with a proper index.

## Filtering by metadata

With many documents in one collection, `where` narrows the search:

```python
collection.query(query_texts=["vacation"], n_results=3, where={"source": "handbook.md"})
```

You'll use metadata for **sources** in the next topics: showing the user which document each answer came from.

## The approximate part

HNSW is *approximate* nearest-neighbour search. On 5 chunks it's exact. On millions it may very occasionally miss a true neighbour in exchange for big speed-ups. For RAG that's almost always a good trade.
