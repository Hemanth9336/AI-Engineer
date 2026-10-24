---
type: lesson
title: "Ranking many candidates, worked through"
minutes: 8
---

Five FAQ titles, one query that shares no keywords with the right answer.

```python
import math

from openai import OpenAI

client = OpenAI()


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


faq = [
    "How do I reset my password?",
    "What are your opening hours?",
    "How do I cancel my subscription?",
    "Where is my order?",
    "Can I pay with PayPal?",
]
query = "I want to stop paying every month"

vectors = [d.embedding for d in client.embeddings.create(model="lab-embed", input=faq + [query]).data]
faq_vecs, query_vec = vectors[:-1], vectors[-1]

scored = sorted(zip((cosine(query_vec, v) for v in faq_vecs), faq), reverse=True)
for score, text in scored[:3]:
    print(f"{score:.4f}  {text}")
```

```text
0.6261  How do I cancel my subscription?
0.3410  Can I pay with PayPal?
0.2103  How do I reset my password?
```

"Stop paying every month" and "cancel my subscription" share no words, yet it's the clear winner. Notice the second result: "pay" is related to "paying", so it gets a middling score - it's ranked, but well below the real match.

## One call, not six

The query rides along in the same batch as the candidates (`faq + [query]`), then the last vector is split off. One embedding request instead of six.

## The pattern you will reuse

```python
scored = sorted(zip(scores, texts), reverse=True)[:k]
```

Pair each score with its text, sort the pairs descending, slice. Every retriever in this course - your own, Chroma, LangChain - does this underneath.
