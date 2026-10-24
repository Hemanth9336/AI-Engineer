---
type: lesson
title: "Cost math per request"
minutes: 5
---

Customers ask one question before any other: **"What will this cost us per month?"** The math is simple once you think in tokens.

## The formula

Providers price input and output tokens separately, per million tokens:

```text
cost per request = input_tokens  / 1,000,000 x input_price
                 + output_tokens / 1,000,000 x output_price
```

Output tokens usually cost **3-5x** more than input tokens.

## A worked example

A support assistant: each request sends a system prompt, three retrieved chunks and the question - about **2,500 input tokens** - and gets back about **300 output tokens**. Prices for a mid-size model: **$0.40** per million input, **$1.60** per million output.

```text
input:  2,500 / 1,000,000 x 0.40 = $0.00100
output:   300 / 1,000,000 x 1.60 = $0.00048
per request                      = $0.00148
```

400 agents x 30 requests a day x 30 days = **360,000 requests/month**:

```text
360,000 x $0.00148 = $532.80 per month
```

Swap in a large model at $3.00 / $15.00 per million and the same workload costs **$6,300** a month. Same requests - 12x the bill. That's why model choice is a business decision.

## Where the tokens hide

| Source | Why it grows |
|---|---|
| System prompt | Sent on **every** request |
| Retrieved documents | k chunks x chunk size, every request |
| Conversation history | Grows with every turn unless trimmed |
| Output | Long answers, reasoning tokens on reasoning models |
| Retries | A failed JSON parse that retries doubles that request |

## Estimate from measurements, not guesses

Run 20-50 realistic requests, read `usage` from each, and average. Then multiply by volume. Always show the customer the **assumptions** (requests per day, tokens per request, price) alongside the total, so they can change one and see the effect.
