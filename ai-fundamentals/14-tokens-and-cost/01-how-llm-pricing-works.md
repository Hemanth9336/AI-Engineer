---
type: lesson
title: "How LLM pricing works"
minutes: 7
---

Hosted LLMs are billed **per token**, with separate prices for what you send and what the model writes.

## Input and output are priced differently

Prices are quoted per **million tokens** (1M). A typical mid-tier model in 2026 might cost:

| | Price per 1M tokens |
|---|---|
| Input (your prompt and history) | $0.80 |
| Output (the model's reply) | $4.00 |

Output is usually **3-5x more expensive** than input, because generating each token is the expensive part. These numbers are examples - always check your provider's pricing page, since prices fall often.

## The formula

```text
cost = prompt_tokens / 1,000,000 x input_price
     + completion_tokens / 1,000,000 x output_price
```

A request with 1,200 input tokens and 300 output tokens at the prices above:

```text
1200 / 1e6 x 0.80 = $0.00096
 300 / 1e6 x 4.00 = $0.00120
                    --------
                    $0.00216
```

About a fifth of a cent. Tiny - until you multiply it by a million requests.

## Things that change the bill

- **Model tier.** Small models can be 20-50x cheaper than frontier ones.
- **Reasoning tokens.** Reasoning models bill their hidden thinking as output tokens.
- **Prompt caching.** Many providers discount input tokens that repeat across requests (a long, fixed system prompt), often by 50-90%.
- **Batch APIs.** Jobs that can wait hours are often half price.
- **Images and files.** These are converted to tokens too, sometimes a lot of them.

## Local models

With Ollama (the `ollama` profile), there is no per-token bill - you pay in hardware, electricity, and speed instead. Tokens still matter: they decide how long you wait.

## Budget before you build

Estimate before you ship: typical input size x typical output size x expected requests per day. If the number surprises you, change the model, shorten the prompt, or cache. The next lesson shows exactly where the token counts come from.
