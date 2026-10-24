---
type: lesson
title: "Validating and retrying"
minutes: 5
---

JSON mode gives you valid JSON. A **schema** says what *correct* JSON looks like, and a **validator** checks it.

## JSON Schema

```python
SCHEMA = {
    "type": "object",
    "required": ["order_id", "issue", "urgency"],
    "additionalProperties": False,
    "properties": {
        "order_id": {"type": ["string", "null"], "pattern": "^MER-[0-9]{5}$"},
        "issue": {"enum": ["damaged", "late", "lost", "address", "billing", "other"]},
        "urgency": {"enum": ["low", "medium", "high"]},
    },
}
```

The `jsonschema` package lists every problem:

```python
from jsonschema import Draft202012Validator

def validate(obj):
    return [e.message for e in Draft202012Validator(SCHEMA).iter_errors(obj)]

validate({"order_id": "MER-55120", "issue": "broken", "urgency": "very high"})
# ["'broken' is not one of ['damaged', ...]", "'very high' is not one of ['low', 'medium', 'high']"]
```

## Retry with the error

When validation fails, don't just ask again - **tell the model what was wrong**. Append its bad reply and a user message with the errors:

```python
messages += [
    {"role": "assistant", "content": raw},
    {"role": "user", "content": f"Your JSON failed validation: {errors}. Reply again with corrected JSON only."},
]
```

Models fix their own mistakes well when given the exact error. Cap the attempts - **three** is a common choice - and decide the fallback: return `None`, flag the ticket for a human, or use a safe default. Never loop forever.

## Make it testable

Separate the **retry logic** from the **API call** by passing the calling function in:

```python
def extract_with_retry(ticket, ask, max_attempts=3):
    ...   # ask(messages) -> raw reply text
```

Now you can test the retry loop with a fake `ask` that returns bad JSON first - no model, no cost, fully repeatable. The checker for this task does exactly that.
