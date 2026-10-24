---
type: lesson
title: "Asking for JSON reliably"
minutes: 5
---

Providers offer API settings that make the model's output parseable.

## JSON mode

```python
resp = client.chat.completions.create(
    model="lab-mini",
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": "Extract fields from the ticket. Reply with a JSON object with keys order_id, issue, urgency."},
        {"role": "user", "content": ticket},
    ],
)
data = json.loads(resp.choices[0].message.content)
```

`response_format={"type": "json_object"}` constrains the output to **valid JSON** - no wrappers, no fences. Two rules:

- **The prompt must still mention JSON** and describe the fields. Some providers reject JSON mode if the word "JSON" isn't in the messages.
- **JSON mode guarantees syntax, not shape.** You'll get valid JSON, but field names and values can still be wrong.

## Structured outputs (JSON schema)

Some providers go further and accept a schema:

```python
response_format={
    "type": "json_schema",
    "json_schema": {"name": "ticket", "strict": True, "schema": TICKET_SCHEMA},
}
```

The model is constrained to that exact shape. Support varies by provider and model - your gateway passes it through when the provider supports it. JSON mode works almost everywhere, which is why this topic uses it plus your own validation.

## Prompt tips for extraction

- **Name every field and its allowed values**: `issue is one of: damaged, late, lost, address, billing, other`.
- **Say what to do when information is missing**: `use null if the ticket has no order id`. Otherwise the model will invent one.
- **Give one example object** in the system prompt.
- **Use temperature 0** - extraction should be repeatable.
