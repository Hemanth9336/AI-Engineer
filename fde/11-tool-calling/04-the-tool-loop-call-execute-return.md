---
type: lesson
title: "The tool loop: call, execute, return"
minutes: 5
---

A tool call is only half a conversation. To get the final answer you send the result back - and the model may ask for another tool. That repeat is the **tool loop**.

```python
messages = [{"role": "user", "content": question}]
while True:
    resp = client.chat.completions.create(model="lab-fast", tools=TOOLS, messages=messages)
    msg = resp.choices[0].message
    if not msg.tool_calls:
        print(msg.content)          # final answer
        break
    messages.append(msg)            # the assistant's tool-call message, exactly as returned
    for call in msg.tool_calls:
        args = json.loads(call.function.arguments)
        result = run_tool(call.function.name, args)
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,          # links the result to the call
            "content": json.dumps(result),
        })
```

## The three rules

1. **Append the assistant message with its `tool_calls`** before the results. The API rejects a tool result that doesn't follow a matching call.
2. **One `tool` message per call**, each with the matching `tool_call_id`. A model may request several calls in one reply.
3. **Send the result as a string** - usually JSON. Keep it small: return the fields the model needs, not the whole database row.

## Run tools safely

`run_tool` is your code, so it's where safety lives:

```python
def run_tool(name, args):
    if name == "get_weather":
        return get_weather(**args)
    return {"error": f"unknown tool {name}"}
```

- **Dispatch by name from a fixed table** - never `eval` or run whatever name the model sends.
- **Validate arguments** before using them.
- **Return errors as results** (`{"error": "unknown city"}`) instead of crashing. The model can then apologise or ask the user.
- **Cap the loop** (you'll do this in the agents section) so a confused model can't call tools forever.
