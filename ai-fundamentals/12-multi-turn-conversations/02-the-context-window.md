---
type: lesson
title: "The context window"
minutes: 7
---

Every model has a **context window**: the maximum number of tokens it can handle in one request - the input (all messages) **plus** the output it writes.

## Sizes in 2026

| Class | Typical window |
|---|---|
| Small local models | 8K - 128K tokens |
| Mainstream hosted models | 128K - 400K tokens |
| Long-context models | 1M tokens or more |

A token is roughly three-quarters of an English word, so 128K tokens is about a 300-page book. Your lab models' windows depend on which provider profile you chose - run `ailab models` to see what each alias points to, and check that model's documentation.

## What happens when you hit the limit

- The API returns an **error** (context length exceeded) if the input alone is too big.
- If the input fits but leaves little room, the **output is cut off** - `finish_reason: "length"`.
- Chat apps silently **drop or summarize** old turns for you. With the raw API, that is your job.

## Bigger is not free

Even when everything fits, long contexts have costs:

1. **Money.** You pay for every input token, every turn.
2. **Speed.** More input means a slower first token.
3. **Attention.** Models are best at using information near the start and end of the context; details buried in the middle of a huge prompt are more likely to be missed. Researchers call this "lost in the middle".

## Rule of thumb

Send what the model **needs** for this turn, not everything you have. A focused 2K-token prompt usually beats a 200K-token dump - and costs a hundredth as much. The next lesson covers how to keep a long conversation focused.
