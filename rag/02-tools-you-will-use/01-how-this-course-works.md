---
type: lesson
title: "How this course works"
minutes: 8
---

Every topic follows the same rhythm: a short lesson, a **worked example** you can run as-is, then a **task** where you do the same thing yourself, then a quick check. By the end you will have built a full RAG system three different ways.

## Your lab machine

The course runs on the same Ubuntu practice machine as AI Fundamentals, plus a few RAG pieces. If you haven't set it up, follow the **RAG skill** section of the [setup guide](../../setup/README.md) - one install script.

| Piece | What it is | You use it for |
|---|---|---|
| Lab AI gateway, `http://localhost:4000` | One OpenAI-compatible endpoint for every model | All model calls |
| `lab-fast` (and `lab-mini`, `lab-smart`) | Chat models behind the gateway | Writing grounded answers |
| `lab-embed` | A local embedding model (all-MiniLM-L6-v2, 384 numbers per text) | Turning text into vectors - free, runs on the VM |
| `/root/ai-lab/.venv` | Python with `openai`, `chromadb`, `langchain`, `langchain-chroma`, `langchain-text-splitters` | Every script you write |
| `/root/rag-lab/NN-<topic>` | One work folder per topic | Your code and data |
| `/root/answers` | Answer files the checkers read | Graded results |

Check it is all alive:

```bash
ailab status       # gateway and embeddings both answering?
ailab test         # one tiny request per model, including lab-embed
```

## Keys stay out of your code

Your environment already holds `OPENAI_BASE_URL` (the gateway) and `OPENAI_API_KEY` (a lab key). The OpenAI SDK reads both automatically, so your scripts never contain a key or a URL. Every checker fails if your lab key shows up in a file.

## How Submit works

Each task ends with **Check your work**: a script you paste into the VM. It reads the files you produced, **runs your scripts on inputs you haven't seen**, and reads the gateway's request log (which records model, client and token counts - never your text). Every line should show ✅ before you press **Submit**.

## The running example

Most topics use small documents from a fictional company called **Northwind**: an employee handbook, ops docs about deploys and backups, support tickets, and a runbook. They are short on purpose, so you can read every word and check the answers yourself.

Next: calling a model from a Python script - the one skill every later topic builds on.
