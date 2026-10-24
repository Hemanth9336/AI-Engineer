---
type: lesson
title: "Clear instructions beat clever tricks"
minutes: 5
---

You'll find "magic prompt" tricks all over the internet: "take a deep breath", "you are a world-class expert", "I'll tip you $200". Some helped old models a little. None of them beat the boring thing: **say exactly what you want**.

## Write it like a brief for a new colleague

Imagine handing the task to a smart temp who knows nothing about the customer. What would they need?

| Element | Vague | Clear |
|---|---|---|
| Task | "Summarize this ticket" | "Summarize this support ticket for the agent who picks it up next" |
| Audience | (none) | "The reader is a support agent with 30 seconds" |
| Format | (none) | "Exactly three lines: `Issue:`, `Customer wants:`, `Urgency:`" |
| Constraints | (none) | "Urgency is one of low, medium, high. Under 40 words total" |
| What to avoid | (none) | "Don't apologise or add advice" |

## Before and after

```text
Summarize this ticket.
```

```text
You summarize support tickets for Meridian Logistics agents. Reply with exactly three lines:
Issue: <what went wrong, max 12 words>
Customer wants: <the outcome they asked for, max 12 words>
Urgency: <low, medium or high>
Use high if the customer mentions a deadline, a refund, or a damaged item. No other text.
```

The second prompt is longer, but every line removes a guess. Output becomes consistent, which means your code can rely on it and your evals can measure it.

## Habits that work

- **Put instructions in the system message** and the data (the ticket) in the user message.
- **Mark where data starts and ends** - for example `<ticket>...</ticket>` - so the model can't confuse a ticket's text with your instructions.
- **Say what to do, not only what not to do.** "Reply in plain sentences" works better than "don't use markdown".
- **Define every judgement word.** What makes something "urgent" at *this* customer?
- **Test on several real inputs**, not the one you wrote the prompt for.
