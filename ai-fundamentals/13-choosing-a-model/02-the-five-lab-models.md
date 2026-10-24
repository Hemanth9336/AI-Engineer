---
type: lesson
title: "The five lab models"
minutes: 7
---

The lab gateway gives you five **aliases**. Each alias points to a real model, chosen by the provider profile you picked in `ailab setup`. Your code always uses the alias, so it keeps working if the model behind it changes.

## The aliases

| Alias | Role | Use it for |
|---|---|---|
| `lab-mini` | Smallest, cheapest | Classification, extraction, quick yes/no checks |
| `lab-fast` | Everyday default | Most tasks in this course |
| `lab-smart` | Strongest general model | Hard writing, reviews, tricky code |
| `lab-reasoning` | Thinks before answering | Maths, planning, multi-step problems |
| `lab-open` | An open-weights model | Seeing how open models compare |

## What is behind them

Run this on your lab machine:

```bash
ailab models
```

It prints each alias and the real model ID it maps to - for example with the `openrouter` profile, `lab-smart` points to a Claude Sonnet model and `lab-reasoning` to an OpenAI reasoning model. With the `ollama` profile, all five run on your own machine.

## The response tells you which one answered

The `model` field in every response shows the alias you called, and the request log records it:

```bash
ailab log 5
```

## Reasoning models behave differently

`lab-reasoning` uses hidden "thinking" tokens before it writes the answer. You pay for them - they show up in `usage.completion_tokens` (and sometimes in `completion_tokens_details.reasoning_tokens`). Two practical effects:

- Give it a generous `max_tokens`, or the thinking can use up the budget and the visible answer comes back empty with `finish_reason: "length"`.
- It is slower. Do not use it for simple lookups.

## Rule of thumb for the lab

Start with `lab-fast`. Move **down** to `lab-mini` if it is good enough and you need it cheaper or faster. Move **up** to `lab-smart` or `lab-reasoning` only when `lab-fast` really fails.
