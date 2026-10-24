---
type: lesson
title: "Meaning as numbers"
minutes: 5
---

Customer documents are text, and computers compare numbers. An **embedding** turns a piece of text into a list of numbers - a **vector** - so that texts with similar **meaning** get similar vectors.

```text
"Report damage within 7 days"        -> [0.021, -0.113, 0.087, ..., 0.042]   (384 numbers)
"How do I claim for a broken parcel?" -> [0.019, -0.098, 0.091, ..., 0.037]   (close to the first)
"Support is open 8:00 to 18:00"       -> [-0.064, 0.012, -0.031, ..., 0.105]  (far from both)
```

The two damage sentences share almost no words, yet their vectors are close. That's the point: embeddings capture meaning, not spelling. It's why a customer asking "my parcel arrived broken" can find the article titled "Reporting a damaged parcel".

## How you get one

An **embedding model** is a separate, much smaller model than a chat model. You call it through the API:

```python
resp = client.embeddings.create(model="lab-embed", input=["Report damage within 7 days", "Support hours"])
vectors = [d.embedding for d in resp.data]     # one vector per input, in order
```

- Send **many texts in one call** - it's faster and cheaper than one call each.
- Every vector from the same model has the same length (`lab-embed`: 384).
- Embeddings are cheap - typically 10-100x cheaper than chat tokens.
- **Never mix models**: vectors from two different embedding models aren't comparable.

## Comparing vectors: cosine similarity

The standard measure is **cosine similarity**: 1 means same direction (same meaning), around 0 means unrelated.

```python
import math

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))
```

Real scores are rarely near 1 or 0. With small models like `lab-embed`, related texts often score 0.4-0.8 and unrelated ones 0.0-0.3. What matters is the **ranking**: which text scores highest for this query.
