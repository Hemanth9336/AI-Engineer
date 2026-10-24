---
type: lesson
title: "Embedding the chunks"
minutes: 6
---

Chunks are ready; now give each one a vector. This is a batch job: read all chunks, embed them in **one** call, save the vectors next to the IDs and text.

```python
import json

from openai import OpenAI

client = OpenAI()
chunks = json.load(open("chunks.json"))

resp = client.embeddings.create(model="lab-embed", input=[c["text"] for c in chunks])
records = [
    {"id": c["id"], "text": c["text"], "embedding": d.embedding}
    for c, d in zip(chunks, resp.data)
]
json.dump(records, open("vectors.json", "w"))
print(f"{len(records)} chunks embedded, {len(records[0]['embedding'])} dimensions")
```

```text
5 chunks embedded, 384 dimensions
```

## Order is guaranteed

`resp.data` comes back in the same order as `input`, so `zip(chunks, resp.data)` pairs each chunk with its own vector. (Each item also has an `index` field if you want to be extra careful.)

## Big document sets

The lab allows 2,048 texts per call; hosted providers have similar caps. For more chunks, embed in batches:

```python
BATCH = 256
vectors = []
for i in range(0, len(texts), BATCH):
    resp = client.embeddings.create(model="lab-embed", input=texts[i:i + BATCH])
    vectors += [d.embedding for d in resp.data]
```

## Index once, query many times

Embedding all chunks is the expensive part, and it only needs to happen when documents change. That's why RAG has two phases:

| Phase | When | What |
|---|---|---|
| **Indexing** | Once, and again when documents change | chunk -> embed -> store |
| **Querying** | Every question | embed the question -> search -> answer |

`vectors.json` is your first, simplest index. Next topic, you'll put it in a real store.
