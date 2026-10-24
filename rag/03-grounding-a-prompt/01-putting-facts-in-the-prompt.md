---
type: lesson
title: "Putting facts in the prompt"
minutes: 8
---

In topic 01 you saw the trick: put the document in the prompt, then ask. This topic turns that trick into a reliable technique called **grounding** - making the model answer from a source you provide.

## The prompt is the model's whole world

For one request, the model knows two things: what it learned in training, and what is in the prompt. Grounding means making the prompt the **only** source that matters for this answer.

## Three parts, in this order

```text
1. Instructions   - how to use the document
2. The document   - clearly marked off
3. The question   - what to answer
```

In the chat API, the first two go in the **system** message and the question goes in the **user** message:

```python
system = (
    "Answer the question using only the document inside <document> tags.\n\n"
    "<document>\n" + document + "\n</document>"
)
messages = [
    {"role": "system", "content": system},
    {"role": "user", "content": question},
]
```

## Why mark off the document

Tags like `<document>` ... `</document>` tell the model exactly where your source starts and stops. That matters because documents are messy: they contain their own questions, headings, even sentences that look like instructions ("Please update this page"). Inside the tags, it's all just **data**.

## Why the document goes before the question

Models read top to bottom. Seeing the document first, then the question, is like a person reading the page before the exam question - the answer is already in mind when the question arrives. It also lets you keep the question short and clear at the very end.

## How much to put in

Only what helps. A focused page beats a whole wiki: it's cheaper, faster, and the model is less likely to miss the important line. Finding "the right page" automatically is exactly what retrieval (topics 04-09) is for. For now, you pick the document by hand.

Next: the two rules that make a grounded answer safe to trust.
