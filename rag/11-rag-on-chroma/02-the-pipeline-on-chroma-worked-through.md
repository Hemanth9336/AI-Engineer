---
type: lesson
title: "The pipeline on Chroma, worked through"
minutes: 11
---

Here are the retrieve and generate steps, now with Chroma doing retrieval. Indexing is the same `upsert` you wrote in topic 09, with one ID per chunk and the file name as `source`.

```python
def answer(question, k=4):
    res = collection.query(query_texts=[question], n_results=k)
    hits = list(zip(res["documents"][0], res["metadatas"][0]))

    context = "\n\n".join(f'<document source="{m["source"]}">\n{d}\n</document>' for d, m in hits)
    system = (
        "Answer the question using only the documents below. "
        f"If they do not contain the answer, reply exactly: {REFUSAL}\n\n{context}"
    )
    resp = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": question}],
    )
    text = resp.choices[0].message.content.strip()
    if "don't know based on the documents" in text.lower():
        return {"question": question, "answer": REFUSAL, "sources": []}
    return {"question": question, "answer": text, "sources": list(dict.fromkeys(m["source"] for _, m in hits))}
```

Compare it with topic 10's version: the `retrieve` function shrank to one `collection.query` line. Everything from `context = ...` down is the same.

## Run it

```bash
python rag_chroma.py index
python rag_chroma.py ask "How many connections may applications open in total?"
```

```text
8 chunks in the docs collection
{
  "question": "How many connections may applications open in total?",
  "answer": "Applications may open at most 500 connections in total.",
  "sources": ["databases.md", "access.md", "oncall.md", "deploys.md"]
}
```

## Use it from Python

```python
from rag_chroma import answer

result = answer("How do I report a phishing email?", k=2)
print(result["answer"])
print(result["sources"])      # ['security.md', ...]
```

That's the shape every RAG service has underneath: an index function, an answer function, and thin wrappers for the command line, an HTTP API or a chat UI.
