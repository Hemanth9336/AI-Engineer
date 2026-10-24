---
type: lesson
title: "Why models hallucinate"
minutes: 5
---

A **hallucination** is a fluent, confident answer that is wrong or invented. It isn't a bug that a future version will simply remove. It follows directly from next-token prediction.

## The model always produces something

The model's job is to continue text plausibly. Ask "What is the warranty period for the Meridian X200 pallet scanner?" and the most likely continuation of that question is an answer that *sounds like* a warranty period - "The Meridian X200 comes with a two-year limited warranty." If the model never saw that product, the probabilities still produce a plausible-looking answer. Nothing inside it checks the facts.

## Common causes at customers

| Cause | Example |
|---|---|
| The fact was never in training data | Internal products, policies, people, prices |
| The fact is too rare or too recent | A niche regulation, last month's price change |
| The question assumes something false | "Why did we stop shipping to Norway?" when you never did |
| The prompt pushes for an answer | "Always give a definite answer" |
| Long, specific details | Exact numbers, dates, citations, URLs |

## How to spot one

- **Ask the same question several times at a higher temperature.** Real knowledge tends to come back the same each time; invented details change between runs - a different warranty period each time is a strong warning sign.
- **Ask for the source.** Invented answers often come with invented sources.
- **Check against a document you trust.**

## What actually reduces them

You can't make a model know everything. You *can*:

1. **Give it the facts** in the prompt (RAG), so the likely continuation is the true one.
2. **Give it permission to say "I don't know"** - an explicit, preferred way out.
3. **Measure** how often it's wrong on a test set, instead of trusting a demo.

You'll do all three in this skill. First, see one happen.
