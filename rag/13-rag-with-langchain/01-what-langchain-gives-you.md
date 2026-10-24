---
type: lesson
title: "What LangChain gives you"
minutes: 6
---

You've built RAG by hand twice. You know every moving part. **LangChain** is a popular open-source framework that packages those parts as ready-made, swappable building blocks - and that's how many teams write RAG at work.

## The building blocks map to what you built

| You built | LangChain block | Package |
|---|---|---|
| `chunk_text()` | `RecursiveCharacterTextSplitter` | `langchain-text-splitters` |
| `client.embeddings.create(...)` | `OpenAIEmbeddings` | `langchain-openai` |
| SQLite / Chroma code | `Chroma` vector store | `langchain-chroma` |
| `retrieve(question, k)` | `store.as_retriever(search_kwargs={"k": k})` | `langchain-core` |
| The grounded prompt string | `ChatPromptTemplate` | `langchain-core` |
| `client.chat.completions.create(...)` | `ChatOpenAI` | `langchain-openai` |
| `.choices[0].message.content` | `StrOutputParser` | `langchain-core` |

A chunk with metadata is a **`Document`**: `page_content` (the text) plus a `metadata` dict (`{"source": "handbook.md"}`).

## Chains with the pipe operator

LangChain's components are **Runnables**: everything has `.invoke(input)`, and you connect them with `|`, like a shell pipeline:

```python
chain = prompt | llm | StrOutputParser()
chain.invoke({"context": "...", "question": "..."})
```

The output of each step is the input of the next. This style is called **LCEL** (LangChain Expression Language).

## Why use it

- **Swap parts in one line**: Chroma to pgvector, `lab-fast` to another provider, a different splitter - the rest of the chain stays.
- **Better building blocks**: the recursive splitter cuts at headings and paragraphs instead of mid-word.
- **Shared vocabulary**: retrievers, documents and chains are common ground in tutorials, job descriptions and codebases.

## Why you built it by hand first

A framework hides the steps. When a LangChain bot gives a bad answer, you'll know where to look - the split, the retriever's k, the prompt - because you've written each of them yourself. Under the hood it's the same math and the same prompt.

## It all goes through your gateway

`ChatOpenAI` and `OpenAIEmbeddings` use the OpenAI SDK underneath, so they read `OPENAI_BASE_URL` and `OPENAI_API_KEY` like your own scripts, and every call shows up in the gateway's request log.
