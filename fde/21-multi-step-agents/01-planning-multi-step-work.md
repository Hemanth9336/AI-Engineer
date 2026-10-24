---
type: lesson
title: "Planning multi-step work"
minutes: 5
---

Some questions need several tool calls **in sequence**, where each call depends on the previous result:

```text
Can I collect order MER-81234 today, and until what time?
```

1. `track_parcel("MER-81234")` -> held at depot **RTM-01**
2. `depot_hours("RTM-01")` -> opens 07:00, closes **18:00**
3. Answer: "Yes - it's at Rotterdam Waalhaven, open until 18:00 today."

The model can't call `depot_hours` first: it doesn't know the depot until the order lookup returns. Your tool loop already supports this - after each result the model may call another tool - but whether it plans well depends on how you set it up.

## Helping the model plan

- **Tool descriptions that state dependencies**: "Today's opening hours for a depot, **by depot id like RTM-01**" tells the model it needs an id first.
- **Return the ids the next step needs**: `track_parcel` returns `"depot": "RTM-01"`, not just "held at the Rotterdam depot".
- **A system prompt hint for common sequences**: "Look up an order's depot before answering questions about collecting it."
- **Stronger models for longer chains**: small models handle one or two hops well; long chains often need a bigger model.

## Make the loop testable

So far the loop has called the OpenAI SDK directly. For an agent, testing matters more: you want to simulate a tool failing or a model that never stops, without a real model. Inject the model call, as you did with `ask` in topic 10:

```python
def run_agent(question, ask):
    messages = [...]
    while True:
        reply = ask(messages)        # -> {"content": ..., "tool_calls": [{"id", "name", "arguments"}]}
        ...
```

`openai_ask` adapts the SDK's response to that simple dict. A test can pass a scripted `ask` that returns whatever sequence it likes.

## Trace every step

Print each tool call (to stderr, or a log). With multi-step agents, "why did it answer that?" is answered by reading the trace: which tools, in what order, with what results.
