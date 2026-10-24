---
type: lesson
title: "Coverage: easy, hard, and out of scope"
minutes: 5
---

A golden set full of easy questions scores 98% and tells you nothing. Real traffic has three kinds of question, and your set needs all three:

| Slice | What it tests | Example |
|---|---|---|
| **Easy** | The common, direct questions - the bulk of the volume | "When is support open?" |
| **Hard** | Inference, combining facts, odd phrasing, edge cases | "Tracking hasn't moved since Monday and it's Thursday - what do I do?" |
| **Trap** (out of scope) | Plausible questions the docs **don't** answer - the bot must refuse | "How much does DDP cost?" |

## Why traps matter most

Traps are where hallucinations live. A question that sounds answerable, about the customer's domain, with related documents nearby, is exactly when a model fills in a plausible fee or deadline. Easy questions can't reveal that. Good traps are:

- **On-topic** - about shipping, not about football. Off-topic questions are easy to refuse.
- **Near a real document** - "How much does DDP cost?" sits right next to the customs article that mentions DDP but no price.
- **Tempting** - a number, a yes/no, a policy that sounds like it should exist.

For a trap, the expected answer is the refusal sentence, and `source` is `null`.

## Report per slice

Never report one blended number. "94% overall" can hide "60% on hard questions" or "two traps answered with invented fees". Report each slice:

```text
easy  38/40   hard  9/12   trap  8/8
```

A reasonable starting mix is roughly **60% easy, 25% hard, 15% trap** - then adjust to match what users actually ask.
