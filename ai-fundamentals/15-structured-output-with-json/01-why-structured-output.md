---
type: lesson
title: "Why structured output"
minutes: 8
---

So far, replies have been text for a person to read. Most real applications need replies that **a program** reads: a label to route a ticket, fields to fill a form, a status for a dashboard. For that you want **structured output** - usually JSON.

## Prose is hard to parse

Ask "What host, port, and status does this alert describe?" and you might get:

```text
The alert is about db-01, which is running on port 5432. Its status
appears to be degraded due to replication lag.
```

Readable - and a nightmare for code. Regexes break on the next phrasing.

## JSON is easy

```json
{"host": "db-01", "port": 5432, "status": "degraded"}
```

One line of code reads any field:

```bash
jq -r .status reply.json
```

```python
data = json.loads(reply)
if data["status"] != "up": page_someone(data["host"])
```

## Where structured output is used

| Use | Example fields |
|---|---|
| Classification | `label`, `confidence` |
| Extraction | Invoice `number`, `date`, `total` from an email |
| Routing | `team`, `priority` |
| Agents and tools | The arguments for a function call (topic 16) |
| Evaluation | `score`, `reason` when one model grades another |

## The two risks

1. **Invalid JSON** - a stray sentence, a Markdown code fence, a trailing comma. `json.loads` fails.
2. **Valid JSON, wrong content** - a missing key, `"5432"` as a string instead of a number, an invented status value like `"slow"`.

The next lesson covers how to prevent the first with API settings and the second with clear instructions - and why you still validate both in code.
