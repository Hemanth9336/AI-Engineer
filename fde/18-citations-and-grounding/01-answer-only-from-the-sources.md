---
type: lesson
title: "Answer only from the sources"
minutes: 5
---

A RAG system's promise is: **answers come from the customer's documents**. The prompt has to make that promise enforceable, because the model's default is to be helpful - which includes filling gaps with whatever it learned in training.

## Where ungrounded answers come from

- **Gaps in the sources**: retrieval found related articles, but none has the specific fact. The model fills in a plausible one.
- **General knowledge leaking in**: "What are typical customs fees?" - the model knows *something* about customs in general, and blends it with the customer's policy.
- **Pressure in the question**: "Just give me your best estimate" invites a guess.

For a support bot, a plausible invented fee or deadline is worse than no answer - a customer acts on it, and the customer's company is liable.

## The grounding prompt

```text
Answer the question using only the sources below.
If the sources don't contain the answer, reply exactly: I don't know based on the provided sources.
Do not use outside knowledge, even if you are confident.
```

Three properties make it work:

1. **"Only the sources"** sets the rule.
2. **An exact refusal sentence** gives the model a sanctioned, easy way out - and lets your code detect it (show a "talk to a human" button, count the refusal rate).
3. **Explicitly forbidding outside knowledge** closes the "but I know this" loophole.

## Partial answers

The hardest case: the sources answer *part* of the question. "How long do customs checks take and how much does DDP cost?" - the sources give the time but not the price. Tell the model what to do: answer the part that's covered and say which part isn't. Decide with the customer which behaviour they want, then test for it.

## Test it with questions you know aren't covered

You can't see grounding on easy questions. Build a handful of **trap questions** - plausible, on-topic, but not answered by any document - and check that every one gets the refusal. You'll formalise this in the golden-datasets topic.
