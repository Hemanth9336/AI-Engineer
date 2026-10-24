---
type: lesson
title: "Defining a tool: name, parameters, description"
minutes: 5
---

A tool definition is JSON the model reads to decide **when** to call the tool and **how** to fill in its arguments. In the OpenAI-compatible format:

```python
TRACK_TOOL = {
    "type": "function",
    "function": {
        "name": "track_parcel",
        "description": "Look up the delivery status of a Meridian order by its order id (like MER-12345). "
                       "Use it for any question about where an order is.",
        "parameters": {                      # a JSON Schema
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Order id, for example MER-55120"},
            },
            "required": ["order_id"],
        },
    },
}
```

Pass a list of them with the request: `tools=[TRACK_TOOL]`.

## Each part matters

| Part | What the model uses it for | Tips |
|---|---|---|
| `name` | Identifying the call | Verb plus noun, snake_case: `track_parcel`, `create_ticket` |
| `description` | Deciding **when** to call | Say what it does **and when to use it**. This is a prompt - write it carefully |
| `parameters` | Filling in arguments | JSON Schema: types, `enum` for fixed choices, a description with an example for each field |
| `required` | Which arguments must be present | Only truly required ones; give optional ones a stated default |

## Common mistakes

- **Vague descriptions** ("gets data") - the model won't know when to use it, or will use it for everything.
- **Overlapping tools** - `get_order` and `lookup_order` with similar descriptions confuse the model. Merge them or make the difference explicit.
- **Free-text parameters where an enum fits** - `"status": "string"` invites "Shipped", "shipped" and "on its way".
- **Too many tools** - accuracy drops as the list grows. Offer only the tools relevant to this assistant.

## Reading the tool call

```python
msg = resp.choices[0].message
if msg.tool_calls:
    call = msg.tool_calls[0]
    name = call.function.name                       # "track_parcel"
    args = json.loads(call.function.arguments)      # {"order_id": "MER-55120"}
```

`arguments` is a JSON **string** - parse it, and validate it like any other model output.
