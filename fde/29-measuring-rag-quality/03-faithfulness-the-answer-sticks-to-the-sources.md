---
type: lesson
title: "Faithfulness: the answer sticks to the sources"
minutes: 5
---

Retrieval found the right article. Did the answer stay inside it? **Faithfulness** (also called groundedness) measures whether every claim in the answer is supported by the sources that were sent:

```text
Source [a1]: Claims are reviewed within 3 working days and approved claims are refunded to the original payment method.
Answer:      Approved claims are refunded within 24 hours [a1].
```

The citation is valid, the topic is right, the tone is fine - and "24 hours" appears nowhere in the source. That's an unfaithful answer, and the most dangerous kind: it *looks* grounded.

## Faithfulness vs correctness

| | Compares the answer to | Catches |
|---|---|---|
| **Correctness** (topic 27) | The expected answer in the golden set | Wrong or missing facts on known questions |
| **Faithfulness** | The retrieved sources | Invented details, even on questions with no golden answer |

Faithfulness needs no expected answer, so you can run it on **live traffic** samples, not just the golden set.

## How to judge it

Ask a judge model to **list unsupported claims**, not just say yes or no:

```json
{"faithful": false, "unsupported": ["approved claims are refunded within 24 hours"]}
```

The list is what makes the verdict trustworthy and debuggable. Treat any non-empty list as unfaithful, even if the judge said `true` - a judge that contradicts itself shouldn't get the benefit of the doubt.

## RAG triad

Together with retrieval hit rate and answer correctness, faithfulness completes a common trio: **did we fetch the right thing, did we stick to it, and was the result right?**
