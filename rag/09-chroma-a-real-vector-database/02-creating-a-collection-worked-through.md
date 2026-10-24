---
type: lesson
title: "Creating a collection, worked through"
minutes: 7
---

Connect Chroma to your gateway's `lab-embed`, create a collection, and add chunks.

```python
import json
import os

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

embed = OpenAIEmbeddingFunction(
    api_key_env_var="OPENAI_API_KEY",
    api_base=os.environ["OPENAI_BASE_URL"],
    model_name="lab-embed",
)

client = chromadb.PersistentClient(path="db")
collection = client.get_or_create_collection(
    "handbook",
    embedding_function=embed,
    configuration={"hnsw": {"space": "cosine"}},
)

chunks = json.load(open("chunks.json"))
collection.upsert(
    ids=[c["id"] for c in chunks],
    documents=[c["text"] for c in chunks],
    metadatas=[{"source": "handbook.md", "index": c["index"]} for c in chunks],
)
print(collection.count(), "chunks in", collection.name)
```

```text
5 chunks in handbook
```

## Line by line

- **`OpenAIEmbeddingFunction`** works with any OpenAI-compatible endpoint. `api_key_env_var` names the variable to read the key from - the key itself stays out of your code. Chroma calls `lab-embed` through your gateway, so these calls show up in the request log.
- **`PersistentClient(path="db")`** saves to the `db/` folder. (`chromadb.Client()` is in-memory and forgets everything when the script ends.)
- **`get_or_create_collection`** is safe to re-run. The `cosine` space is fixed when the collection is first created - to change it, delete and recreate the collection.
- **`upsert`** inserts new IDs and replaces existing ones - the same idempotence as your `INSERT OR REPLACE`. You pass **documents**, and Chroma embeds them for you in batches.

## Look at what's stored

```python
print(collection.get(ids=["handbook-003"], include=["documents", "metadatas"]))
```

```text
{'ids': ['handbook-003'], 'documents': ['ryption and lock after five minutes ...'],
 'metadatas': [{'index': 3, 'source': 'handbook.md'}], ...}
```

The `db/` folder now holds a small SQLite file plus the vector index. Run the script again: still 5 chunks.
