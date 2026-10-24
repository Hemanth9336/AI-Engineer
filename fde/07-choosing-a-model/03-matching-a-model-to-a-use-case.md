---
type: lesson
title: "Matching a model to a use case"
minutes: 5
---

There's no "best model". There's the right model **for this workload**. Ask four questions:

1. **How hard is the task?** Classifying a ticket into five categories is easy. Reconciling two contracts clause by clause is hard.
2. **Who's waiting?** A person in a live chat needs a fast answer. A nightly batch job can wait.
3. **How much volume?** 50 requests a day barely registers on any bill. 2 million a month makes every cent per request matter.
4. **What does a mistake cost?** A slightly awkward ticket summary is harmless. A wrong figure in a regulatory report is not.

## Typical matches

| Workload | Usually a good fit | Why |
|---|---|---|
| Ticket classification, routing, extraction | Small | Easy, high volume, easy to check |
| Live support chat over retrieved documents | Mid | Needs good reading and tone, fast |
| Contract review, complex analysis | Large | Hard, low volume, costly mistakes |
| Multi-step planning, tricky maths or code | Reasoning | Benefits from thinking first; latency acceptable |
| Data must stay on the customer's servers | Open model, self-hosted | Deployment constraint beats everything |

## The selection rule

Write the requirements as numbers, then choose mechanically:

> Pick the **cheapest** model whose quality meets the minimum **and** whose latency fits the limit.

Quality comes from your evals (later in this skill); latency from measurements like the race you just ran; cost from the price list. When a model only just misses the quality bar, the fix is often a better prompt or better retrieval - not a bigger model.

## Mixing models is normal

Production systems often use several: a small model to classify the question, a mid model to answer most of them, and a large model only for the hard ones. That's **routing**, covered in the cost-control topic.
