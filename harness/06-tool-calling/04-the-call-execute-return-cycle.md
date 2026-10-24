---
type: lesson
title: "The call, execute, return cycle"
minutes: 6
---

A tool call is only half a conversation. To get an answer, your harness runs the tool and sends the result back. One round trip is a **cycle**:

```python
messages = [{"role": "user", "content": question}]
resp = client.chat.completions.create(model="lab-fast", tools=TOOLS, messages=messages)
msg = resp.choices[0].message

if msg.tool_calls:
    messages.append(msg)                     # 1. the assistant's tool-call message, as returned
    for call in msg.tool_calls:
        args = json.loads(call.function.arguments)
        result = run_tool(call.function.name, args)          # 2. execute
        messages.append({"role": "tool",                     # 3. return
                         "tool_call_id": call.id,
                         "content": result})
    resp = client.chat.completions.create(model="lab-fast", tools=TOOLS, messages=messages)

print(resp.choices[0].message.content)
```

After one cycle the history looks like this:

```text
user       What version are we releasing?
assistant  tool_calls: [read_file(path="files/release.txt")]   id call_ab12
tool       (tool_call_id call_ab12) "version: 2.3.0\nfreeze: Friday"
assistant  We're releasing 2.3.0; the code freeze is on Friday.
```

## The three rules

1. **Append the assistant message with its `tool_calls`** before any results. A `tool` message that doesn't follow a matching call is rejected.
2. **One `tool` message per call**, with the matching `tool_call_id`. A model may ask for several calls in one reply.
3. **Content is a string.** Plain text or JSON - keep it to what the model needs.

## Execute safely

`run_tool` is your code, so it's where the harness earns its name:

```python
def run_tool(name, args):
    if name == "read_file":
        return read_file(**args)
    return f"error: unknown tool {name}"
```

- **Dispatch from a fixed table** - never `eval` the name or run whatever the model sends.
- **Return errors as text** (`error: no such file`) instead of crashing. The model reads them and can recover (topic 09).
- One cycle is enough for one tool. When the model needs several steps, you'll wrap this in a loop (topic 07).
