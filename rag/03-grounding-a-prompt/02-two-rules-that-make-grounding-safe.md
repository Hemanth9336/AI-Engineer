---
type: lesson
title: "Two rules that make grounding safe"
minutes: 8
---

A document in the prompt makes good answers possible. Two short rules make them **trustworthy**.

## Rule 1: only the document

Say it explicitly: **answer using only the document**. Without this rule the model blends the document with what it learned in training. That sounds helpful, and it is a trap:

- Public knowledge may **contradict** your document. ("Most companies give 25 vacation days" - yours gives 20.)
- The answer stops being **checkable**. You can't tell which sentence came from your source.

With the rule, every claim in the answer should trace back to a line in the document.

## Rule 2: an exact sentence for "not there"

The document won't always contain the answer. Tell the model exactly what to say then:

```text
If the document does not contain the answer, reply exactly:
I don't know based on the document.
```

Why **exactly** that sentence?

1. **No guessing.** You've given the model a respectable way out, so it doesn't fill the gap with something plausible.
2. **Code can detect it.** `if answer == "I don't know based on the document."` - your program can then show a different message, log the gap, or try another source.
3. **You can test it.** In topic 12 you'll measure how often your system refuses correctly.

## The full prompt

```text
Answer the question using only the document inside <document> tags.
If the document does not contain the answer, reply exactly:
I don't know based on the document.

<document>
...
</document>
```

## Partial answers

Sometimes the document answers half the question. A good habit is to answer the part you can and say what's missing - but for anything a program reads, keep the refusal rule strict: either the answer is in the document, or you get the exact sentence.

## What grounding doesn't fix

Grounding can't make a wrong document right. If the runbook is out of date, the answer will be faithfully out of date. Keep sources current - and later, show which source each answer came from.
