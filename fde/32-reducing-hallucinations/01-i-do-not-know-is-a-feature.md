---
type: lesson
title: "I do not know is a feature"
minutes: 5
---

Customers often see "I don't know" as a failure. For a support or policy assistant, it's the opposite: **a confident wrong answer is the worst outcome, and a clean refusal is a good one.**

| Outcome | Cost to the customer |
|---|---|
| Correct answer | None - the goal |
| "I don't know - here's how to reach the team" | One routed conversation |
| Plausible invented fee, deadline or policy | A customer acts on it; complaints, refunds, liability, lost trust in the whole system |

## Make abstaining easy for the model

Hallucinations get more likely when the model has nothing good to work with. Two layers stop that:

1. **Don't ask when there's nothing to answer from.** If retrieval's best score is below a threshold, there are no relevant sources. Return the refusal **without calling the model** - it's cheaper, faster and can't hallucinate.
2. **Give the model a sanctioned way out.** The exact refusal sentence from topic 18, plus an explicit instruction for partial coverage: answer what the sources cover and say what they don't.

```python
sources = [a for score, a in scored(question)[:3] if score >= min_score]
if not sources:
    return REFUSE          # no model call
```

## Make the refusal useful

A bare "I don't know" frustrates users. Pair it with a next step in the UI: a button to contact support, a link to the help centre, a handoff to a human agent. Because the refusal is an exact sentence, your code can detect it and show the button.

## Sell it to the customer

Frame refusals as **safety and honesty**: "When the documents don't cover it, the assistant says so and hands over to your team." Then show the trap-question results (next task). Most compliance teams relax when they see it.
