---
type: lesson
title: "Why free text breaks pipelines"
minutes: 5
---

A chat reply is written for a human. A pipeline needs data: an order ID to look up, a category to route on, a number to compare. When code consumes model output, free text breaks in predictable ways.

Ask for JSON in plain words and you'll usually get it - but "usually" includes:

````text
Sure! Here's the JSON you asked for:
```json
{"order_id": "MER-55120", "city": "Leeds"}
```
Let me know if you need anything else!
````

`json.loads()` on that raises `JSONDecodeError`. Other common failures:

| Failure | Example |
|---|---|
| Chatty wrapper | "Sure! Here's..." around the JSON |
| Markdown fences | A json code fence around the object |
| Invalid JSON | Single quotes, trailing commas, comments |
| Wrong field names | `orderId` instead of `order_id` |
| Wrong types | `"urgency": 3` instead of `"high"` |
| Missing fields | No `city` when the ticket doesn't mention one |
| Invented values | A plausible order ID that isn't in the ticket |

Each of these is rare per request. At 10,000 requests a day, rare means dozens of failures daily - each one a stuck ticket, a crashed job, or a wrong record.

## The fix comes in layers

1. **Ask the API for JSON** (JSON mode or structured outputs) - removes wrappers and invalid syntax.
2. **Validate against a schema** - catches wrong names, types, values and missing fields.
3. **Retry with the error**, then fall back - handles the leftovers.

You'll build each layer in this topic. First, see the failure happen.
