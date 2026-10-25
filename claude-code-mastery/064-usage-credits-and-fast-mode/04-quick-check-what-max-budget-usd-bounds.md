---
type: quiz
title: "Quick check: what --max-budget-usd bounds"
minutes: 11
---

### Q1. `claude -p ... --max-budget-usd 0.50` reaches the cap. What happens?

- A. The bill is capped for the month
- B. The model switches to haiku
- C. That one run stops with subtype error_max_budget_usd and is_error true
- D. It keeps going and warns

<details><summary>Answer</summary>

**Answer: C** - It's a per-run ceiling, not an account limit.

</details>

### Q2. A cron job runs 300 times a night with `--max-budget-usd 0.50`. What's the most it can spend in a night?

- A. $0.50
- B. $5
- C. Unlimited
- D. About $150, the cap times the number of runs

<details><summary>Answer</summary>

**Answer: D** - Per-run caps multiply; account-level spend limits and alerts cover the total.

</details>

### Q3. A session is slow because each turn waits 3 minutes for the test suite. Will `/fast` help?

- A. Yes, a lot
- B. Only with opus
- C. It halves the test time
- D. Barely - fast mode speeds up token generation, not tool execution

<details><summary>Answer</summary>

**Answer: D** - Compare duration_api_ms with duration_ms before paying for speed.

</details>

### Q4. Your claude.ai chat this morning used a lot of your plan. Does it affect Claude Code this afternoon?

- A. No, they're separate
- B. Yes - subscription usage is shared across Claude surfaces
- C. Only on Team plans
- D. Only on weekends

<details><summary>Answer</summary>

**Answer: B** - One allowance covers chat, desktop, and Claude Code.

</details>

### Q5. `modelUsage` on an expensive run lists your main model plus a small model you never selected. What's the small one?

- A. An error
- B. A different user's run
- C. Background calls Claude Code makes on a small model, such as summaries and titles
- D. Fast mode

<details><summary>Answer</summary>

**Answer: C** - Background tokens are real tokens; they're usually small, but check them when costs surprise you.

</details>
