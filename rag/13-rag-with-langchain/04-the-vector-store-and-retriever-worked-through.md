---
type: lesson
title: "The vector store and retriever, worked through"
minutes: 6
---

LangChain's `Chroma` wraps the same Chroma database you used in topic 09 - with LangChain's embedding object instead of Chroma's.

```python
import json

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="lab-embed", check_embedding_ctx_length=False)
store = Chroma(
    collection_name="handbook",
    embedding_function=embeddings,
    persist_directory="db",
    collection_configuration={"hnsw": {"space": "cosine"}},
)

splits = json.load(open("splits.json"))
docs = [Document(page_content=s["text"], metadata={"source": s["source"]}) for s in splits]
store.add_documents(docs, ids=[s["id"] for s in splits])
print(len(store.get()["ids"]), "chunks")
```

```text
5 chunks
```

- **`check_embedding_ctx_length=False`** - by default `OpenAIEmbeddings` pre-tokenises text with OpenAI's tokenizer and sends token numbers. Your lab model (like most non-OpenAI models) expects plain text, so turn that off.
- **`add_documents(..., ids=...)`** upserts: same IDs, no duplicates on re-runs.
- **`collection_configuration`** sets the cosine space when the collection is created, exactly as in topic 09.

## The retriever

A **retriever** is a Runnable that takes a question and returns `Document`s:

```python
retriever = store.as_retriever(search_kwargs={"k": 3})
for d in retriever.invoke("Can I work from another country?"):
    print(d.id, d.metadata["source"], d.page_content[:40].replace("\n", " "))
```

```text
handbook-002 handbook.md ## Remote work You can work from home
handbook-004 handbook.md ## Leaving the company Give four weeks
handbook-000 handbook.md # Northwind Employee Handbook  ## Wor
```

That's your topic 08 `search()` function - embed the question, find the k nearest - as a reusable component you can drop into a chain.

## Scores, if you want them

The retriever returns documents only. To see scores, ask the store directly:

```python
store.similarity_search_with_relevance_scores("Can I work from another country?", k=3)
# [(Document(...handbook-002...), 0.491), ...]       relevance = 1 - cosine distance
```

## Keep it in a module

Put the store and a `get_retriever(k)` function in one file, `retriever.py`. The chain in the next lesson imports it - and so could an eval script or an API.
