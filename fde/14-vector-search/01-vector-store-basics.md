---
type: lesson
title: "Vector store basics"
minutes: 5
---

A **vector store** keeps each text next to its embedding so you can search later without re-embedding everything. At its simplest it's a list of records:

```json
[
  {"id": "a1", "text": "Reporting a damaged parcel. Report damage within 7 days...", "embedding": [0.021, -0.113, ...]},
  {"id": "a2", "text": "Changing a delivery address. You can change...", "embedding": [-0.004, 0.071, ...]}
]
```

## What each record needs

| Field | Why |
|---|---|
| `id` | A stable identifier: for citations, updates and deletes |
| `text` | What you'll send to the model as context |
| `embedding` | What you search with |
| metadata (later) | Source, date, owner, **who may see it** - for filtering |

## Build time vs query time

| Build time (once, or when documents change) | Query time (every question) |
|---|---|
| Read and chunk documents | Embed the question |
| Embed chunks in batches | Score against stored vectors |
| Save records | Return the top results |

## From a JSON file to a database

A JSON file is perfect for learning and for a few thousand chunks: no setup, easy to inspect. Customers with more data use a **vector database** - Chroma, pgvector in PostgreSQL, Pinecone, Weaviate, Elasticsearch, or the vector search built into their cloud. They add:

- **Fast approximate search** (indexes like HNSW) over millions of vectors.
- **Metadata filters** - "only documents this user may see".
- **Updates and deletes** without rewriting a file.
- Persistence, backups and access control.

The concepts don't change: records with ids, text, vectors and metadata; embed the query; get the top matches. At a customer, prefer the database they already run - pgvector inside their existing PostgreSQL is often easier to get approved than a new service.
