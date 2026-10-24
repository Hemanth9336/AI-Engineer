---
type: lesson
title: "Swapping the store"
minutes: 11
---

Your pipeline has three parts with clear jobs. Because they only meet at small interfaces, you can replace one without touching the others.

| Part | Interface | Your version | Swap to |
|---|---|---|---|
| Chunker | text -> list of chunks | `chunk_text()` | LangChain splitters (topic 13) |
| Store + retrieval | upsert(chunks); query(question, k) -> chunks | SQLite + flat cosine | **Chroma** |
| Generator | question + chunks -> answer | Grounded prompt to `lab-fast` | Any chat model |

## What changes when the store becomes Chroma

| | SQLite version | Chroma version |
|---|---|---|
| Embedding the chunks | You call `lab-embed`, store JSON | Chroma calls `lab-embed` for you on upsert |
| Search | Load every vector, cosine in Python | `collection.query(query_texts=[q], n_results=k)` |
| Sources | A `source` column | `metadatas=[{"source": ...}]` |
| Scale | Thousands of chunks | Millions, with HNSW |

The **generate** phase doesn't change at all: it still receives a list of (text, source) pairs.

## Make it a library, not just a command

In topic 10, `rag.py` was a command-line tool. This time you'll expose two **functions** so other code - a web app, a Slack bot, an eval script (topic 12) - can use your RAG:

```python
index_docs() -> int          # number of chunks in the collection
answer(question, k=4) -> dict
```

and `answer()` returns structured data instead of printing:

```json
{
  "question": "When is a written postmortem due?",
  "answer": "A written postmortem is due within five business days.",
  "sources": ["incidents.md", "deploys.md", "oncall.md", "backups.md"]
}
```

A dict is easy to turn into JSON for an API, to log, and to test. The command-line part becomes a thin wrapper around these functions.

## Paths that work from anywhere

When another script imports your module from a different folder, relative paths like `"db"` point somewhere else. Build paths from the module's own location:

```python
from pathlib import Path

HERE = Path(__file__).resolve().parent
client = chromadb.PersistentClient(path=str(HERE / "db"))
```
