---
type: lesson
title: "Not all models are equal"
minutes: 7
---

"Which AI should I use?" has no single answer. Models differ on several axes at once, and the best choice depends on the job.

## The axes that matter

| Axis | What varies | Why you care |
|---|---|---|
| **Capability** | Reasoning, coding, following complex instructions | Hard tasks fail on small models |
| **Speed** | Time to first token, tokens per second | Interactive tools need snappy replies |
| **Cost** | Price per million input and output tokens | Differences of 10-50x between tiers |
| **Context window** | 8K to 1M+ tokens | Long documents need room |
| **Modalities** | Text only, or images, audio, files | Screenshots and PDFs need a vision model |
| **Openness** | Closed API, or open weights you can run | Privacy, control, offline use |

## Tiers, not brands

Every major provider offers a ladder:

- **Small / mini / nano** - fast and very cheap. Great for classification, extraction, short rewrites.
- **Mid-size / flash / fast** - the everyday default: good quality, good price.
- **Frontier / large** - the strongest at hard reasoning, long writing, tricky code. Slower and pricier.
- **Reasoning** - spend extra "thinking" tokens before answering. Best for maths, planning, multi-step logic.

The tier usually matters more than the brand. A small model from any good provider beats a frontier model on cost; a frontier model from any good provider beats a small one on hard problems.

## Benchmarks are a starting point

Public leaderboards measure models on standard tests. They are useful for a shortlist, but your task is not a benchmark. The only reliable test is **your prompts, on your data, compared side by side** - which is exactly what this topic's task does.

## Models change fast

New versions appear every few months, and names get retired. Build so you can swap models easily: keep the model name in one config value, not scattered through your code. In this lab, aliases like `lab-fast` do that for you.
