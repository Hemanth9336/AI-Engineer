---
type: lesson
title: "Asking a model for JSON"
minutes: 8
---

There are three levels of control, from weakest to strongest. Use as many as your model supports.

## Level 1: ask in the prompt

Describe the exact shape, with types and allowed values:

```text
Reply with only a JSON object, no other text, with these keys:
- "host": string
- "port": number
- "status": one of "up", "degraded", "down"
```

Works with any model, but nothing guarantees it. Models may still wrap the JSON in a code fence or add "Here is the JSON:".

## Level 2: JSON mode

Most chat completion APIs accept:

```json
"response_format": {"type": "json_object"}
```

The model is now constrained to produce **valid JSON**. Two rules:

- You must **still describe the keys** in the prompt - JSON mode guarantees syntax, not your schema.
- Most providers require the word **"JSON"** to appear somewhere in your messages when JSON mode is on.

## Level 3: structured outputs with a schema

Newer APIs accept a full JSON Schema:

```json
"response_format": {
  "type": "json_schema",
  "json_schema": {"name": "status", "strict": true, "schema": {
    "type": "object",
    "properties": {
      "host":   {"type": "string"},
      "port":   {"type": "integer"},
      "status": {"type": "string", "enum": ["up", "degraded", "down"]}
    },
    "required": ["host", "port", "status"],
    "additionalProperties": false
  }}
}
```

With `strict: true`, supported models must follow the schema exactly. Support varies by provider and model, so check before relying on it; SDKs often let you pass a Pydantic class or Zod schema instead of raw JSON.

## Always validate

Whatever level you use, the response content is still a **string**. Parse it and check it:

```bash
jq -r '.choices[0].message.content' response.json > reply.json
jq -e '.port | type == "number"' reply.json
```

If parsing or validation fails, retry once with the error message, then fail loudly. Never pass unvalidated model output into a database, a shell command, or another system.

## Tip: give it an escape hatch

If the input may not contain a value, say what to do: `"use null if the alert does not say"`. Otherwise the model will invent something plausible.
