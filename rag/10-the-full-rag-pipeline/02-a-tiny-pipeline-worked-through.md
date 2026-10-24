---
type: lesson
title: "A tiny pipeline, worked through"
minutes: 10
---

The whole pipeline fits in one file. Here it is over two documents, kept in memory so you can see every step at once.

```python
import math

from openai import OpenAI

client = OpenAI()
REFUSAL = "I don't know based on the documents."

docs = {
    "parking.md": "Staff parking is in garage B. Visitors park in garage A and get a ticket at reception.",
    "lunch.md": "The canteen serves lunch from 11:30 to 14:00. Friday is pizza day.",
}


def embed(texts):
    return [d.embedding for d in client.embeddings.create(model="lab-embed", input=texts).data]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


# 1. index
names = list(docs)
vectors = embed([docs[n] for n in names])

# 2. retrieve
question = "Where should visitors park?"
qv = embed([question])[0]
hits = sorted(zip((cosine(qv, v) for v in vectors), names), reverse=True)[:1]

# 3. generate
context = "\n\n".join(f'<document source="{n}">\n{docs[n]}\n</document>' for _, n in hits)
system = (
    "Answer the question using only the documents below. "
    f"If they do not contain the answer, reply exactly: {REFUSAL}\n\n{context}"
)
resp = client.chat.completions.create(
    model="lab-fast",
    temperature=0,
    messages=[{"role": "system", "content": system}, {"role": "user", "content": question}],
)
print(resp.choices[0].message.content)
print("Sources:", ", ".join(n for _, n in hits))
```

```text
Visitors park in garage A and get a ticket at reception.
Sources: parking.md
```

Each numbered comment is one phase. The real version you'll build next adds three things:

1. **Chunking** the documents (topic 07) instead of embedding whole files.
2. **A store** on disk (topic 08), so indexing runs once and asking runs many times.
3. **A command-line interface**: `python rag.py index` and `python rag.py ask "..."`.

## Two commands, two phases

```bash
python rag.py index                                 # phase 1 - run when docs change
python rag.py ask "How do I roll back a bad release?"  # phases 2 and 3 - every question
```

Separating them matters: indexing is slow and costs embedding calls for every chunk; asking is fast and embeds only the question.
