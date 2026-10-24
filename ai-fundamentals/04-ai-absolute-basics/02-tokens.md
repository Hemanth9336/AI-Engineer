---
type: lesson
title: "Tokens"
minutes: 6
---

Models do not read letters or whole words. They read **tokens**: chunks of text from a fixed vocabulary of roughly 100,000 to 200,000 pieces. Every prompt you send is split into tokens, and every reply comes back one token at a time.

## What a token looks like

A tokenizer splits text into the pieces it knows. Common words are often one token; rarer words are split into several:

```text
"The server restarted"      ->  "The" | " server" | " restarted"          3 tokens
"Kubernetes"                ->  "K" | "ubern" | "etes"                     3 tokens
"unbelievably"              ->  "un" | "belie" | "vably"                   3 tokens
"2026-10-24"                ->  "202" | "6" | "-" | "10" | "-" | "24"      6 tokens
```

The exact splits depend on the model family - OpenAI, Anthropic, and Google each use their own tokenizer - so the same sentence can be 10 tokens for one model and 12 for another.

## Rules of thumb for English

| Amount of text | Roughly |
|---|---|
| 1 token | 4 characters, or three-quarters of a word |
| 100 tokens | 75 words |
| 1,000 tokens | 750 words, about a page and a half |
| 1 million tokens | a long shelf of books |

Other languages, source code, JSON, and long numbers usually take **more** tokens per word than plain English prose.

## Why it explains some odd failures

Because the model sees chunks, not letters, tasks that depend on individual characters are surprisingly hard:

- Counting the letters in a word ("how many r's in strawberry?")
- Reversing a string, or spelling a rare word backwards
- Exact arithmetic on long numbers that were split into odd pieces

The model never saw "s-t-r-a-w-b-e-r-r-y" one letter at a time. When a job needs exactness at the character or digit level, hand it to real code.

## You will see tokens in every reply

From topic 05 on, every API response you get includes a **usage** block like this:

```json
"usage": { "prompt_tokens": 18, "completion_tokens": 42, "total_tokens": 60 }
```

`prompt_tokens` is everything you sent. `completion_tokens` is what the model wrote back. Next lesson: why those two numbers matter so much.
