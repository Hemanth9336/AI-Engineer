---
type: lesson
title: "A simple LangChain agent"
minutes: 8
---

LangChain v1 builds agents with one function: `create_agent`. You give it a model, a list of tools, and a system prompt; it runs the tool loop for you.

## Tools are decorated functions

```python
from langchain_core.tools import tool

@tool
def get_service_status(service: str) -> str:
    """Get the current health of one production service, e.g. checkout."""
    return '{"status": "degraded", "error_rate": "4.2%"}'
```

The `@tool` decorator turns the function into a tool definition:

- the **function name** becomes the tool name,
- the **type hints** become the argument schema,
- the **docstring** becomes the description the model reads to decide when to use it.

So the docstring is part of the prompt - write it carefully.

## Creating and running the agent

```python
import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="lab-fast", base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"])

agent = create_agent(
    llm,
    tools=[get_service_status],
    system_prompt="You are an on-call assistant. Use tools for live data. Never guess a status.",
)

result = agent.invoke({"messages": [{"role": "user", "content": "Is checkout healthy?"}]})
print(result["messages"][-1].content)
```

`result["messages"]` holds the whole run: the question, each tool call, each tool result, and the final answer. Print them all when debugging:

```python
for m in result["messages"]:
    print(type(m).__name__, getattr(m, "tool_calls", None) or m.content)
```

## Logging tool calls

In production you want a record of every action an agent took. The simplest approach is to log inside each tool:

```python
def log_call(name, **args):
    with open("agent-tools.log", "a") as f:
        f.write(f"tool={name} args={args}\n")
```

## Limits

Cap how long an agent can run: `agent.invoke(..., {"recursion_limit": 10})` stops a run that loops too many times. Now build one.
