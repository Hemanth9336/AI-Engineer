---
type: lesson
title: "Zero-shot vs few-shot"
minutes: 8
---

There are two ways to tell a model what you want: describe it, or show it.

## Zero-shot: describe it

A **zero-shot** prompt gives instructions and no examples:

```text
Classify this support message as billing, outage, or access.
Message: I was charged twice this month.
```

Modern models handle many zero-shot tasks well. But "classify" leaves questions open: Should it answer `billing` or `Billing` or `Category: billing`? Is "I can't log in because my card expired" billing or access? Every model decides differently, and sometimes the same model decides differently twice.

## Few-shot: show it

A **few-shot** prompt includes a handful of worked examples before the real input. The model picks up the pattern - the labels, the format, the judgement calls - and copies it.

Over the API, the cleanest way to give examples is as earlier turns of a conversation: each example is a `user` message with an input and an `assistant` message with the ideal answer.

```json
{"model": "lab-fast", "messages": [
  {"role": "system", "content": "Classify each support message. Reply with one word: billing, outage, or access."},
  {"role": "user", "content": "I was charged twice this month."},
  {"role": "assistant", "content": "billing"},
  {"role": "user", "content": "I reset my password and still can't sign in."},
  {"role": "assistant", "content": "access"},
  {"role": "user", "content": "The dashboard has been blank for everyone since 9am."}
]}
```

The model has just "seen itself" answer two messages with one lower-case word. It will very likely answer the third - `outage` - the same way.

## When to use which

| Use zero-shot when | Use few-shot when |
|---|---|
| The task is common and obvious | The format must be exact every time |
| Any reasonable wording is fine | Labels or categories are your own |
| You want the shortest, cheapest prompt | Edge cases need a consistent judgement call |

Examples cost tokens on every request, so use as few as do the job - usually two to five. Next: how to write examples the model will copy faithfully.
