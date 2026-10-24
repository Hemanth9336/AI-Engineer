---
type: lesson
title: "Setting accuracy expectations"
minutes: 8
---

Every customer eventually asks: "How accurate is it?" Your answer shapes the contract, the rollout and whether the project is judged a success.

## Never promise 100%

LLM systems are probabilistic. Even with grounding, citations and refusals, some answers will be wrong. Promising perfection guarantees a breach of promise. What you **can** promise:

- **A measured accuracy on an agreed eval set**, reported regularly.
- **Behaviour when unsure**: refusals on out-of-scope questions, measured on traps.
- **A process**: every reported error becomes an eval case, fixed and regression-tested.
- **Safeguards proportional to risk**: human review where mistakes are expensive.

## Make "accuracy" precise

| Vague | Precise |
|---|---|
| "It's 95% accurate" | "95 of 100 golden questions answered correctly, as graded by your support leads" |
| "It doesn't hallucinate" | "All 20 trap questions refused; faithfulness 98% on a sample of 200 live answers" |
| "It's better than humans" | "Same correctness as the desk team on the golden set, answering in seconds instead of 2.5 days" |

## Compare with today

Humans make mistakes too. Measure the current process on the same questions when you can. A target like "at least as accurate as the current team, with every answer cited" is fair, achievable and meaningful.

## Match the bar to the risk

| Use | Reasonable bar |
|---|---|
| Internal drafts reviewed by staff | 80-90% correct; refusals on out-of-scope |
| Customer-facing answers, low stakes | 90%+ correct, 100% trap refusal, escalation path |
| Regulated or financial answers | Human approval of every answer, or strictly limited scope |

Write the agreed bar, the eval set and the measurement process into the statement of work. That's the "contract" from topic 25 - made official.
