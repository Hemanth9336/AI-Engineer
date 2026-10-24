---
type: lesson
title: "What is LangChain"
minutes: 8
---

**LangChain** is the most widely used open-source framework for building LLM applications in Python (and JavaScript). It gives you building blocks so you don't rewrite the same plumbing in every project.

## What it provides

| Piece | What it is |
|---|---|
| **Chat models** | One interface for OpenAI, Anthropic, Google, Ollama, and dozens more |
| **Prompt templates** | Prompts with `{placeholders}` you fill in at run time |
| **Output parsers** | Turn the reply into a string, JSON, or a typed object |
| **Tools** | Python functions the model can call |
| **Agents** | Models that call tools in a loop (topic 21) |
| **Retrievers** | Fetch relevant documents for RAG (topic 23) |

Its companion **LangGraph** handles more complex, stateful agent workflows; LangChain's own agents are built on it.

## Swap providers in one line

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

llm = ChatOpenAI(model="lab-fast")
# llm = ChatAnthropic(model="claude-sonnet-4-5")    # same code below works
```

## When to use it - and when not to

LangChain is worth it when you need several pieces together - templates, multiple providers, tools, retrieval, agents - or want its ecosystem of integrations.

For a single API call, the plain SDK (topic 19) is simpler and easier to debug. Many teams start with the SDK and adopt LangChain when the app grows. Both are fine; know what each costs you.

## In the lab

`langchain` and `langchain-openai` are installed in `/root/ai-lab/.venv`. Point `ChatOpenAI` at the gateway and every lab model works:

```python
import os
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="lab-fast", base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"])
print(llm.invoke("Say hello in five words").content)
```
