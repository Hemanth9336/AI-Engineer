---
type: lesson
title: "Model routing: cheap model first"
minutes: 5
---

Topic 4 showed that a large model can cost 10-30x a small one. Most support questions don't need it: "when are you open?" is as well answered by `lab-mini` as by `lab-smart`. **Routing** sends each request to the cheapest model that can handle it.

## Ways to route

| Router | How | Trade-off |
|---|---|---|
| **Rules** | Length, keywords, question type | Free and predictable; crude |
| **Classifier** | A tiny model or embedding classifier labels easy/hard | Better accuracy; one cheap call |
| **Cascade** | Try the small model; escalate if its answer fails a check (refusal, invalid JSON, low faithfulness) | Pays twice on hard questions |
| **By task** | Extraction and classification -> small; multi-step reasoning -> large | Simple when the system has distinct steps |

Start with rules. They're easy to explain to the customer and easy to test.

```python
easy = len(words) <= 12 and question.count("?") <= 1 and not HARD_WORDS & set(words)
model = "lab-mini" if easy else "lab-fast"
```

## Prove it doesn't hurt quality

Routing is a quality decision disguised as a cost decision. Before you ship it:

1. Run the golden set (topic 28) with everything on the large model, and again with routing.
2. Compare per slice - routing errors usually show up on the **hard** slice.
3. Report the saving *and* the quality delta: "62% of traffic moves to the small model, cost down 54%, correctness unchanged on easy, -1 case on hard."

## Watch the mix

Log which model handled each request. If the share of the cheap model drifts (new kinds of questions, a product launch), both cost and quality move with it.
