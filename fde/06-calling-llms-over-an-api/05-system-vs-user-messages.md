---
type: lesson
title: "System vs user messages"
minutes: 5
---

The **system message** is where you, the developer, set the rules. The **user message** is what the end user typed. Keeping them separate is one of the most important habits in this skill.

```python
messages = [
    {"role": "system", "content": "You are Meridian Logistics' support assistant. Support hours are 8:00-18:00 CET, Monday to Friday. Answer in one sentence."},
    {"role": "user", "content": "When can I call support?"},
]
```

## What goes where

| System message | User message |
|---|---|
| Who the assistant is, and for which company | The question |
| Facts it must use (hours, policies, retrieved documents) | Details the user provides |
| Rules: tone, length, format, what to refuse | |
| Fixed for every request | Changes every request |

## Why the split matters

- **Models give system instructions more weight.** They're trained to treat the system message as the developer's rules, which makes behaviour more consistent.
- **Users can't see or easily change it.** The instructions stay yours even when the user writes something odd.
- **It's your product surface.** At a customer, the system prompt *is* most of the product: a few hundred words that decide tone, scope and safety. You'll version and test it like code.

## Not a security boundary

A system message raises the bar, but a determined user (or a malicious document) can still talk a model out of its instructions. That's **prompt injection**, and you'll handle it in the guardrails topic. Never put secrets - passwords, keys, other customers' data - in a system message.

## Without a system message

The model falls back to its generic assistant behaviour: polite, wordy, and with no idea who your customer is. Ask "When can I call support?" with no system message and you'll get general advice about finding a support number. With one, you get the customer's actual hours. You'll see that difference in the task.
