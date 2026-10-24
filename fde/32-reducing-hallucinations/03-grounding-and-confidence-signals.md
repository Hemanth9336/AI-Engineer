---
type: lesson
title: "Grounding and confidence signals"
minutes: 5
---

You can't ask a model "how confident are you?" and trust the number - models are poorly calibrated about their own correctness. But your system produces plenty of signals that *are* useful.

## Signals you already have

| Signal | Where it comes from | Low value suggests |
|---|---|---|
| **Best retrieval score** | Cosine similarity of the top chunk | Nothing relevant was found |
| **Score gap** | Top-1 score minus top-2 | Several half-relevant chunks, none clearly right |
| **Citation validity** | `check_citations` (topic 18) | The answer isn't tied to the sources |
| **Faithfulness check** | A judge or a cheap model (topic 29) | Claims not in the sources |
| **Refusal sentence** | Exact match | The model itself found no answer |
| **Self-consistency** | Ask twice; compare | The model is guessing |

## Use them to route, not to decorate

Showing users "confidence: 0.73" helps nobody. Use signals to **decide**:

- High retrieval score, valid citations -> show the answer.
- Low score -> refuse without calling the model.
- Answer present but faithfulness check fails -> replace with the refusal and log it.
- Refusal -> show "talk to a person".

## Measure it

The metric that matters for hallucinations is how the system behaves on **trap questions**:

- **Abstain rate on traps** - of the questions the docs don't answer, how many got the refusal? Target: as close to 100% as possible.
- **False abstain rate** - of the answerable questions, how many were wrongly refused? Too high and the bot is useless.

Both move together when you change the threshold or the prompt: a stricter system refuses more traps *and* more real questions. Measuring both is how you pick the trade-off - with the customer.
