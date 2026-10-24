---
type: scenario
title: "When fine-tuning is the right call"
minutes: 5
---

Meridian classifies 40,000 support tickets a day into 35 categories with company-specific rules. The current setup uses `lab-smart` with a 4,000-token prompt full of rules and 30 examples. It's 94% accurate on a 500-case golden set, but it costs too much and adds 3 seconds per ticket. They have 60,000 tickets already labelled by agents.

### Q1. Why is fine-tuning reasonable here?

- A. The CTO likes it
- B. It's a narrow, stable classification task with lots of labelled examples, a measured cost and latency problem, and an eval set to prove the result
- C. Fine-tuning is always cheaper
- D. Classification needs no evals

<details><summary>Answer</summary>

**Answer: B** - Every ingredient for a good fine-tuning case is present.

</details>

### Q2. What would you fine-tune?

- A. The biggest model available
- B. A small model on the labelled tickets, aiming to match the large model's 94% with a short prompt
- C. An embedding model
- D. Nothing - just shorten the prompt

<details><summary>Answer</summary>

**Answer: B** - Specialise a small model to cut cost and latency.

</details>

### Q3. What decides whether it goes live?

- A. The training loss
- B. How long training took
- C. A demo to the COO
- D. The same 500-case golden set: it must match or beat 94%, with per-category results checked for regressions

<details><summary>Answer</summary>

**Answer: D** - The existing eval is the bar.

</details>
