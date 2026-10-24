---
type: lesson
title: "A grounded prompt, worked through"
minutes: 8
---

Here is the whole technique in one function, run on a real document.

## The document

```text
Northwind on-call policy
The on-call rotation changes every Monday at 09:00 UTC.
The primary on-call must acknowledge a page within 15 minutes.
On-call engineers get one day off after a week with a night-time page.
```

## The function

```python
from openai import OpenAI

client = OpenAI()
REFUSAL = "I don't know based on the document."


def grounded_answer(document, question):
    system = (
        "Answer the question using only the document inside <document> tags. "
        f"If the document does not contain the answer, reply exactly: {REFUSAL}\n\n"
        f"<document>\n{document}\n</document>"
    )
    resp = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": question}],
    )
    return resp.choices[0].message.content.strip()
```

## Three questions

```python
doc = open("oncall.txt").read()
print(grounded_answer(doc, "When does the on-call rotation change?"))
print(grounded_answer(doc, "How fast must the primary acknowledge a page?"))
print(grounded_answer(doc, "How much is the on-call bonus?"))
```

```text
The on-call rotation changes every Monday at 09:00 UTC.
The primary on-call must acknowledge a page within 15 minutes.
I don't know based on the document.
```

The first two come straight from the document. The third is the important one: the document says nothing about a bonus, and instead of inventing a number, the model gives the exact refusal sentence.

## Normalise before comparing

Models sometimes add a trailing space or drop the full stop. When your code checks for the refusal, compare loosely, then print the exact sentence yourself:

```python
answer = grounded_answer(doc, question)
if "don't know based on the document" in answer.lower():
    answer = REFUSAL
```

That way the output of your tool is always one of two things: a grounded answer, or exactly the refusal.

## Try breaking it

Ask a question whose answer "everyone knows" but the document doesn't say - "What does UTC stand for?". A well-grounded model should refuse, because the rule says *only the document*. That strictness is what makes grounded answers trustworthy.

Your turn.
