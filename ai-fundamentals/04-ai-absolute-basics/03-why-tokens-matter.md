---
type: lesson
title: "Why tokens matter"
minutes: 6
---

Tokens are not just a technical detail. They are the unit that sets **what you pay**, **how much fits**, and **how long you wait**.

## 1. Price

API providers charge per token, usually quoted **per million tokens**, with separate prices for input and output. Output tokens cost more - often three to five times more - because generating is harder than reading.

An illustrative price list (real prices change; always check the provider):

| Model size | Input per 1M | Output per 1M |
|---|---|---|
| Small and fast | $0.10 | $0.40 |
| Mid-size | $0.80 | $4.00 |
| Frontier | $3.00 | $15.00 |

A request that sends 2,000 tokens and gets 500 back on the mid-size model costs:

```text
input:   2,000 / 1,000,000 x $0.80 = $0.0016
output:    500 / 1,000,000 x $4.00 = $0.0020
total:                               $0.0036
```

A third of a cent. Cheap for one call - but run it on 100,000 support tickets and it is $360. Topic 14 shows how to measure and cut this.

## 2. Space: the context window

Every model has a **context window**: the maximum number of tokens it can handle in one request, counting your prompt **and** its reply. Windows range from tens of thousands of tokens to over a million. A long document, a long chat history, and a long answer all compete for the same space. Topic 12 covers what happens when it fills up.

## 3. Time

Models generate one token after another, typically somewhere between 30 and 200 tokens per second. A 50-token answer feels instant; a 3,000-token report takes a while. Long outputs are slow outputs.

## 4. A hard stop: max_tokens

When you call a model from code you set **`max_tokens`**, the most tokens it may write. If it hits that limit mid-sentence, it simply stops, and the response tells you so. Useful as a safety cap on cost, painful if set too low. You will see it happen in topic 05.

## The takeaway

Shorter prompts cost less, shorter answers cost less and arrive sooner, and everything has to fit in the window. Right now, try talking to a model yourself.
