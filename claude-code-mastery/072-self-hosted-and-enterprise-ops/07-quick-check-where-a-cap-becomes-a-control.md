---
type: quiz
title: "Quick check: where a cap becomes a control"
minutes: 8
---

### Q1. Which mechanism stops one developer from spending more than $50 a day through a shared Bedrock credential?

- A. --max-budget-usd 50
- B. availableModels
- C. An AWS budget alert
- D. A gateway spend limit with scope user (or a group default) and period daily

<details><summary>Answer</summary>

**Answer: D** - Per-run caps bound runs and cloud budgets alert on accounts; only the gateway sees each person's requests.

</details>

### Q2. An `rbac_group` cap of $100/day on `contractors` with 20 members. How much can the group spend in a day?

- A. $100 total
- B. Unlimited
- C. $5 each
- D. Up to $100 per member - group caps are per-seat defaults, not a shared pool

<details><summary>Answer</summary>

**Answer: D** - Each member inherits the cap individually.

</details>

### Q3. A developer passes the cap mid-task. What does Claude Code show?

- A. Nothing; it switches models
- B. The gateway's 429 message with the period and reset time (and any blocked_message you set)
- C. A crash
- D. A login prompt

<details><summary>Answer</summary>

**Answer: B** - Requests fail with a billing error that says when it resets; warnings came at 75% and 95%.

</details>

### Q4. Your finance team reconciles gateway spend against the AWS bill and finds a 3% difference. Is the cap broken?

- A. Yes
- B. It means fraud
- C. Only if over 5%
- D. No - the gateway prices requests as an estimate for enforcement; the provider's bill is the invoice

<details><summary>Answer</summary>

**Answer: D** - Caps are a circuit breaker; billing comes from the provider.

</details>

### Q5. A nightly job runs 500 agent runs, each with `--max-budget-usd 1`. Is the job's spend bounded at $1?

- A. Yes
- B. No - it's bounded at about $500; add a per-job total check or a separate capped account
- C. At $0
- D. At $50

<details><summary>Answer</summary>

**Answer: B** - Per-run caps multiply with the number of runs.

</details>
