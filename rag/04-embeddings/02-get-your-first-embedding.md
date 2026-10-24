---
type: lesson
title: "Get your first embedding"
minutes: 10
---

Embeddings come from the same gateway and the same SDK you already use - just a different method.

```python
from openai import OpenAI

client = OpenAI()
resp = client.embeddings.create(
    model="lab-embed",
    input="The payments team deploys every Tuesday at 15:00 UTC.",
)
vector = resp.data[0].embedding
print(len(vector))
print([round(x, 4) for x in vector[:5]])
print(resp.usage.total_tokens)
```

```text
384
[-0.0152, -0.0265, -0.0245, -0.0295, -0.0316]
14
```

- `resp.data[0].embedding` is a plain Python list of 384 floats.
- `usage` shows tokens, as with chat - embeddings are billed by input tokens on paid providers.

## Many texts in one call

`input` also accepts a **list**. You get one embedding per text, in the same order:

```python
texts = ["How do I reset my password?", "I forgot my login password", "Lunch is served at noon"]
resp = client.embeddings.create(model="lab-embed", input=texts)
vectors = [d.embedding for d in resp.data]
print(len(vectors), len(vectors[0]))      # 3 384
```

Always batch when you have many texts: one request with 100 texts is far faster than 100 requests. (Providers cap the batch size - the lab allows 2,048 texts per call.)

## Vectors are normalised

Compute the length of the vector - the square root of the sum of squares:

```python
import math
print(round(math.sqrt(sum(x * x for x in vector)), 4))    # 1.0
```

MiniLM returns vectors of length **1**. Many embedding models do this; it makes comparing them simpler, as you'll see in topic 05.

## Saving an embedding

A vector is just a list, so JSON stores it fine:

```python
import json
json.dump({"text": text, "model": "lab-embed", "embedding": vector}, open("vec.json", "w"))
```

Always store **which model** made it - remember, vectors from different models can't be compared.

## Where to see it

The gateway logs embedding calls like chat calls, with `api: "embeddings"` and an `inputs` count:

```bash
tail -1 /var/log/ailab/requests.jsonl | jq '{api, model, inputs, prompt_tokens}'
```

```json
{ "api": "embeddings", "model": "lab-embed", "inputs": 3, "prompt_tokens": 19 }
```
