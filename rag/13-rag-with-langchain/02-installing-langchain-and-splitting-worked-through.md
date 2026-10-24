---
type: lesson
title: "Installing LangChain and splitting, worked through"
minutes: 6
---

The packages are already in your venv (the RAG install script added them). On another machine you'd run:

```bash
pip install langchain langchain-openai langchain-chroma langchain-text-splitters
```

LangChain is split into small packages: `langchain-core` (the shared interfaces) plus one package per integration. You install only what you use.

## The recursive splitter

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
docs = splitter.create_documents([open("handbook.md").read()], metadatas=[{"source": "handbook.md"}])

print(len(docs), [len(d.page_content) for d in docs])
for d in docs:
    print(repr(d.page_content[:30]))
```

```text
5 [253, 441, 441, 436, 130]
'# Northwind Employee Handbook\n'
'## Vacation\nNew employees get 2'
'## Remote work\nYou can work fr'
'## Laptops and security\nEvery l'
'## Leaving the company\nGive fo'
```

Same size limit as your `chunk_text()`, very different chunks: every chunk now starts at a **heading**.

## How "recursive" works

It tries separators in order - `"\n\n"` (paragraphs), then `"\n"` (lines), then `" "` (words), then single characters - and uses the biggest one that keeps chunks under `chunk_size`. Paragraphs that fit stay whole; only text that's too long gets cut more finely. Overlap is added only where a cut had to happen inside text.

## Does it help? Measure

The same question against both chunkings, scored by cosine similarity:

| Question | Top score, your 500-char windows | Top score, recursive splitter |
|---|---|---|
| How many vacation days do new employees get? | 0.4955 | 0.7000 |
| Can I work from another country? | 0.2689 | 0.4910 |

Chunks that follow the document's structure hold one topic each, so their vectors are sharper and matching questions score much higher. Same embedding model - only the chunking changed.

## Metadata travels

`create_documents(..., metadatas=[...])` copies the metadata onto every chunk, so each `Document` still knows it came from `handbook.md`.
