---
type: lesson
title: "Comparing two sentences, worked through"
minutes: 10
---

Let's put real embeddings through `cosine()`.

```python
import math

from openai import OpenAI

client = OpenAI()


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


texts = [
    "The server is out of disk space.",
    "The disk on the host is full.",
    "Lunch is served at noon.",
]
a, b, c = [d.embedding for d in client.embeddings.create(model="lab-embed", input=texts).data]

print(f"disk vs disk : {cosine(a, b):.4f}")
print(f"disk vs lunch: {cosine(a, c):.4f}")
```

```text
disk vs disk : 0.5976
disk vs lunch: 0.0160
```

The two disk sentences share only the word "disk", yet score 0.60 - the model sees they describe the same problem. The lunch sentence is near zero: unrelated.

## Read the scores as a ranking

0.5976 isn't "60% the same". It's simply **much higher than** 0.0160. If you were searching for "disk full" problems, the first sentence would rank above the second by a wide margin - and ranking is all search needs.

## Make it reusable

You'll compare vectors in every later topic, so keep `cosine()` in a module you can import, and put any demo code behind the main guard:

```python
# similarity.py
def cosine(a, b): ...

if __name__ == "__main__":
    ...   # demo only runs when started directly
```

Then other scripts can do `from similarity import cosine`.
