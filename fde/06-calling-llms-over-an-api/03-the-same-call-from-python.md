---
type: lesson
title: "The same call from Python"
minutes: 5
---

`curl` is great for a quick test. For anything real you'll use the official **`openai` Python package** - and it works with any OpenAI-compatible endpoint, including your lab's gateway, by changing the base URL.

```python
from openai import OpenAI

client = OpenAI()   # reads OPENAI_API_KEY and OPENAI_BASE_URL from the environment

resp = client.chat.completions.create(
    model="lab-mini",
    max_tokens=200,
    temperature=0,
    messages=[{"role": "user", "content": "What does a forward deployed engineer do?"}],
)
print(resp.choices[0].message.content)
print(resp.usage.total_tokens, resp.choices[0].finish_reason)
```

The response is an object, not a dict, so you use dots: `resp.choices[0].message.content`. The structure is the same as the JSON you saw with curl.

## Where the key and URL come from

`OpenAI()` with no arguments reads two environment variables:

| Variable | Your lab sets it to |
|---|---|
| `OPENAI_API_KEY` | your lab key (same as `$LAB_AI_KEY`) |
| `OPENAI_BASE_URL` | `$LAB_AI_URL/v1` |

That's the pattern to use at customers too: code reads configuration from the environment, so the same script runs against a test gateway, a staging key, and production without edits - and the key never sits in the code.

## Errors you'll meet

```python
import openai

try:
    resp = client.chat.completions.create(...)
except openai.AuthenticationError:   # bad key
    ...
except openai.BadRequestError as e:  # bad model name, context too long, invalid parameters
    print(e)
except openai.APIConnectionError:    # gateway or network down
    ...
```

The SDK retries some failures (rate limits, timeouts) automatically - twice by default.
