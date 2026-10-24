---
type: lesson
title: "The description decides everything"
minutes: 6
---

The model never sees your tool's code. It sees a name, a description and a parameter schema - a few dozen words - and from those alone it decides **whether** to call the tool, **when**, and **with what**. Tool definitions are prompts. Usually the most important prompts in the harness.

## Two versions of the same tool

```python
# v1
{"name": "search_logs", "description": "Searches logs.",
 "parameters": {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"]}}
```

```python
# v2
{"name": "search_logs",
 "description": "Search one Stackline service's application logs for lines matching a query. "
                "Use it for any question about errors, timeouts, crashes or slow requests in billing or search. "
                "Returns at most 20 matching lines, newest first.",
 "parameters": {"type": "object", "properties": {
     "service": {"type": "string", "enum": ["billing", "search"], "description": "Which service's logs to search"},
     "query": {"type": "string", "description": "Text to look for, for example timeout or HTTP 500"},
     "since_hours": {"type": "integer", "description": "How far back to look, in hours. Default 24."}},
   "required": ["service", "query"]}}
```

Same code behind both. Very different agent:

| Question | v1 | v2 |
|---|---|---|
| "Any timeouts in search in the last hour?" | Often answers from imagination | `search_logs(service="search", query="timeout", since_hours=1)` |
| "Why did billing return 500s?" | `search_logs(q="why did billing return 500s")` | `search_logs(service="billing", query="500")` |
| "What's the refund policy?" | Sometimes searches the logs for it | Answers or says it doesn't know - not a log question |

## What a good description contains

1. **What it does**, concretely: which data, which system.
2. **When to use it** - the kinds of questions it answers. This is the line most descriptions are missing, and it's what makes the model reach for the tool.
3. **What it returns**, including limits: "at most 20 lines", "newest first", "empty list if none".
4. Optionally, **when not to use it**, if there's a similar tool or a common mistake.

## Parameters are prompts too

Each property's `description`, `enum` and `type` tell the model how to fill it. `"q": {"type": "string"}` invites the whole question pasted in. `"service": {"enum": ["billing", "search"]}` makes a wrong service impossible.

## Test descriptions like code

You can't tell a description is good by reading it. Run the same questions against both versions and count: how often did the model call the tool, and with sensible arguments? That's what you'll build next - a small experiment harness.
