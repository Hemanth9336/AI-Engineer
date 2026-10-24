---
type: lesson
title: "Controlling the output format"
minutes: 5
---

When code consumes the model's output, the format must be **exact**. "Usually right" breaks pipelines at 3 a.m.

## Ways to control format, weakest to strongest

| Technique | How | Reliability |
|---|---|---|
| Describe it | "Reply with one line: P1, P2 or P3" | Good with clear prompts |
| Show it | Few-shot examples | Better |
| Constrain length | `max_tokens`, "under 20 words" | Stops rambling, can cut answers |
| Stop sequences | `stop=["\n"]` - generation ends at the first newline | Guarantees one line |
| JSON mode / structured output | `response_format` (next topic) | Guarantees valid JSON |
| Tool calling | The model fills a defined schema | Strongest for actions |

## Always validate in code

Whatever you ask for, check what you got:

```python
import re

FORMAT = re.compile(r"^(P1|P2|P3)\|(warehouse|billing|delivery)$")

line = reply.strip()
if not FORMAT.match(line):
    raise ValueError(f"unexpected format: {line!r}")
```

A regular expression (`re`) is the simplest exact check for short formats. `^` and `$` anchor the start and end, so extra words fail.

## Make the format easy to produce

- **Prefer short, rigid formats** over long templated prose.
- **Use words the model already uses**: `high` beats `H3`.
- **Give the full allowed set** every time: `one of: warehouse, billing, delivery`.
- **Ask for the label first**, before any explanation - and usually skip the explanation.
- **Handle failure explicitly**: retry, fall back to a default, or flag for a human. Never pass an unchecked value downstream.
