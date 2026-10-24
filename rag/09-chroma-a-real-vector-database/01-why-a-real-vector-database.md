---
type: lesson
title: "Why a real vector database"
minutes: 7
---

Your SQLite store works and you understand every line. A real vector database does the same job and adds what you'd otherwise build yourself:

| You built | A vector database adds |
|---|---|
| Flat search over every row | An **approximate index** (HNSW) - fast at millions of vectors |
| Embeddings as JSON text | Compact binary storage |
| Manual embedding before insert | An **embedding function** - give it text, it embeds for you |
| One table | **Collections** - separate indexes per dataset |
| Just id/text/vector | **Metadata** on every chunk, and filters on it |

## Chroma

**Chroma** is an open-source vector database that runs inside your Python process (or as a server). It's popular for RAG because it starts in two lines and stores everything in a local folder. It's already installed in your venv.

Core vocabulary:

- **Client** - your connection. `chromadb.PersistentClient(path="db")` keeps data in the `db/` folder across runs.
- **Collection** - a named set of chunks, like a table: `handbook`, `support-tickets`. Names need 3-512 characters: letters, digits, `.`, `_` or `-`.
- **Documents** - the chunk texts.
- **IDs** - unique per chunk, exactly like your `handbook-003`.
- **Metadatas** - a small dict per chunk: `{"source": "handbook.md", "index": 3}`.
- **Embedding function** - the model that turns documents and queries into vectors.

## Distance, not similarity

Chroma returns a **distance**: smaller is closer. With the **cosine** space, distance = 1 - cosine similarity:

| Cosine similarity | Cosine distance |
|---|---|
| 1.0 (same) | 0.0 |
| 0.6 | 0.4 |
| 0.0 (unrelated) | 1.0 |

So `similarity = 1 - distance`. Chroma's default space is `l2` (straight-line distance); you'll set `cosine` explicitly so scores match what you've used so far.

## Other vector databases

pgvector (inside PostgreSQL), Qdrant, Weaviate, Pinecone, Milvus and others use the same ideas: collections, IDs, vectors, metadata, top-k queries. Learn one well and the rest are a short read of their docs.
