---
type: lesson
title: "What a token is"
minutes: 5
---

Models don't read characters or words. They read **tokens**: chunks of text from a fixed vocabulary, usually 100,000-200,000 entries. Common words are one token; rare words, names, numbers and codes are split into several.

```text
"Hello!"                    -> ["Hello", "!"]                               2 tokens
"shipping policy"           -> ["shipping", " policy"]                       2 tokens
"MER-88412-XZ"              -> ["MER", "-", "884", "12", "-", "XZ"]          6 tokens
"Rückgaberichtlinie"        -> ["R", "ück", "gabe", "richt", "linie"]        5 tokens
```

(Exact splits differ between model families - each vendor trains its own tokenizer.)

## Rules of thumb

- English prose: about **4 characters** or **0.75 words** per token.
- Code, IDs, timestamps and numbers: **more** tokens per character.
- Many non-English languages: **more** tokens for the same meaning - often 1.5-3x.

So the same request costs different amounts depending on what's in it. A customer whose tickets are full of order IDs and German text will use noticeably more tokens than your English test prompts suggest.

## Why tokens are the unit that matters

Everything about a model is measured in tokens:

| What | Measured in |
|---|---|
| Price | Dollars per million **input** and per million **output** tokens |
| Context window | Maximum tokens per request (prompt + answer) |
| Speed | Output tokens per second |
| `max_tokens` | Cap on output tokens |

## Count the real thing

Tokenizer libraries can estimate counts offline, but the **authoritative** count is the one the API bills you for. Every response includes it:

```python
resp = client.chat.completions.create(model="lab-mini", max_tokens=1, messages=[{"role": "user", "content": text}])
print(resp.usage.prompt_tokens, resp.usage.completion_tokens)
```

`prompt_tokens` also includes a few tokens of message formatting, so even "Hello!" costs a handful. With `max_tokens=1` you measure a prompt for the price of one output token.
