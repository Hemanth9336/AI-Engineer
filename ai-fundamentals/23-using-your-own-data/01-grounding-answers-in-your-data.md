---
type: lesson
title: "Grounding answers in your data"
minutes: 8
---

Out of the box, a model knows the public internet up to its cutoff. It knows **nothing** about your services, your runbooks, your tickets, or your contracts. Ask about them and it will either refuse or - worse - invent something plausible.

**Grounding** means giving the model the source material in the prompt and telling it to answer **only from that material**.

## The grounding prompt

Three parts make it work:

```text
Answer the question using only the document inside <document> tags.
If the document does not contain the answer, reply exactly: NOT IN DOCUMENT

<document>
...your runbook...
</document>
```

1. **The source**, clearly delimited (topic 10).
2. **The restriction**: only from this source - not from general knowledge.
3. **The escape hatch**: an exact reply for "not found", so the model never has to guess - and your code can detect it.

## Make answers checkable

Ask the model to show its evidence:

```text
After the answer, quote the sentence from the document that supports it.
```

A quote is easy to verify with `grep`. If the quote isn't in the document, the answer is suspect.

## Use temperature 0

Grounded Q&A is a factual task. `temperature: 0` keeps the model close to the text.

## Limits of "just paste it in"

Grounding by pasting works well when the source is small: one runbook, one contract, one log. It stops working when:

- the material is **bigger than the context window** (a whole wiki),
- it would be **too expensive** to send everything on every question,
- the relevant part is buried and gets **lost in the middle**.

For those cases you send only the **relevant pieces** - which is what RAG is, next.
