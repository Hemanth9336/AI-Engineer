---
type: lesson
title: "Judge pitfalls"
minutes: 6
---

A judge is a model, so it has a model's habits. Left unchecked, they quietly inflate your scores.

| Pitfall | What it looks like | Fix |
|---|---|---|
| **Verbosity bias** | Long, confident answers pass; short correct ones fail | "Ignore length and tone" in the rubric |
| **Politeness bias** | "Great question! Happy to help!" earns a pass with a wrong fact | Grade facts only |
| **Leniency on numbers** | 14 days vs 7 days is "close enough" | "Fail if any number, deadline or amount differs" |
| **Own knowledge** | The judge "knows" a typical policy and overrides the expected answer | Always pass the expected answer; tell it to trust it |
| **Vague rubric** | "Is it helpful and correct?" means different things each run | Concrete pass and fail conditions |
| **Self-preference** | A model rates its own style higher | Judge with a different (often stronger) model |

## Measure the judge itself

You can't see these biases by reading the rubric. You see them by comparing the judge to **human labels**:

1. Take 20-50 answers and have a domain expert label each pass or fail.
2. Run the judge on the same answers.
3. **Agreement** = cases where judge and human match / total.
4. Read every disagreement. Each one points at a rubric problem.
5. Fix the rubric, re-run, repeat until agreement is high (90%+ is a good target).

Re-check agreement whenever you change the rubric or the judge model. A judge you haven't measured is an opinion, not an eval.
