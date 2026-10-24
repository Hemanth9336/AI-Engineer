---
type: lesson
title: "What makes a good prompt"
minutes: 7
---

A prompt is everything you give the model: the instruction, the context, any examples, and the text to work on. The model cannot ask you clarifying questions before it starts - it fills every gap with its best guess. **A good prompt leaves fewer gaps.**

## Vague versus clear

```text
Vague:  Write something about backups.
```

The model has to guess the audience, the purpose, the length, and the format. It will produce a generic essay that suits nobody.

```text
Clear:  Write a reminder for our engineering team about the new nightly database
        backups. They are developers, not DBAs. Explain when backups run (02:00 UTC),
        where they are stored (the s3://acme-backups bucket), and how to request a
        restore (open a ticket in #ops). Use exactly 4 bullet points, under 80 words.
```

Same topic. The second one gets a usable answer on the first try.

## The five ingredients

| Ingredient | Question it answers | Example |
|---|---|---|
| **Task** | What should it do? | "Write a reminder", "Summarize", "Classify" |
| **Context** | What does it need to know? | The facts, the situation, the source text |
| **Audience** | Who is it for? | "Developers, not DBAs", "a new customer" |
| **Format** | What shape should the answer take? | "4 bullet points", "a table", "JSON" |
| **Constraints** | What limits apply? | "Under 80 words", "no jargon", "only from the text" |

Not every prompt needs all five, but every missing one is a guess the model makes for you.

## A useful test

Imagine handing your prompt to a smart new colleague who knows nothing about your project. Could they do the job without coming back with questions? If not, the model can't either - it just won't ask.

## Clear is not the same as long

Clarity comes from the right details, not from more words. "Be thorough and detailed and comprehensive" adds length and nothing useful. "Cover the three steps in the runbook, one sentence each" adds one precise constraint. Next: the two kinds of message a prompt is built from.
