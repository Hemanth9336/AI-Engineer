---
type: lesson
title: "Defining a tool schema"
minutes: 6
---

A tool definition is the model's only information about a tool. It reads it to decide **when** to call the tool and **how** to fill in the arguments. In the OpenAI-compatible format:

```python
READ_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a text file from the project and return its contents. "
                       "Use it whenever the answer depends on what a file says.",
        "parameters": {                      # a JSON Schema
            "type": "object",
            "properties": {
                "path": {"type": "string",
                         "description": "Path relative to the project folder, for example notes/todo.txt"},
            },
            "required": ["path"],
        },
    },
}
```

Send a list of them with each request: `tools=[READ_FILE_TOOL]`.

## Each part matters

| Part | What the model uses it for | Tips |
|---|---|---|
| `name` | Identifying the call | Verb plus noun, snake_case: `read_file`, `list_dir`, `run_tests` |
| `description` | Deciding **when** to call | Say what it does and when to use it - this is a prompt |
| `parameters` | Filling in arguments | JSON Schema: types, `enum` for fixed choices, an example per field |
| `required` | Which arguments must be present | Only the truly required ones; state defaults for the rest |

## Reading what comes back

```python
msg = resp.choices[0].message
if msg.tool_calls:
    call = msg.tool_calls[0]
    name = call.function.name                       # "read_file"
    args = json.loads(call.function.arguments)      # {"path": "files/release.txt"}
else:
    print(msg.content)                              # the model answered directly
```

`arguments` is a JSON **string**, not a dict. Parse it - and remember the model wrote it, so it can be wrong.

## How the checkers test your tools

Real models vary from run to run, so the checkers in this skill test your harness against **labmock** (`/opt/harness/labmock.py`): a stand-in model that replays a script - "call `read_file` with this path", then "answer with this text". Your code can't tell the difference, because it talks the same API. You'll write scripts for it yourself from topic 30, when you build eval suites.
