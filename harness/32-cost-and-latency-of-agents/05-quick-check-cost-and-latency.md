---
type: quiz
title: "Quick check: cost and latency"
minutes: 4
---

### Q1. Why does a 10-step agent run cost much more than 10 single calls?

- A. Agents use a pricier model
- B. Tool calls cost extra
- C. Every step re-sends the growing history, so earlier tool results are paid for again and again
- D. Output tokens are expensive

<details><summary>Answer</summary>

**Answer: C** - Input tokens compound over steps.

</details>

### Q2. Which step is usually the most expensive?

- A. The first
- B. The final answer
- C. The summarizer call
- D. One late in the run, after big tool results have piled up

<details><summary>Answer</summary>

**Answer: D** - The prompt is largest late in the run.

</details>

### Q3. Why check the token budget before a call, not after?

- A. It's faster
- B. Usage isn't available after
- C. The API requires it
- D. After the call you've already paid for it

<details><summary>Answer</summary>

**Answer: D** - Prevent the spend, don't just record it.

</details>

### Q4. Which calls count toward a task's budget?

- A. Only the main loop
- B. Only tool calls
- C. Only expensive models
- D. All of them: main loop, subagents, verifiers and compaction

<details><summary>Answer</summary>

**Answer: D** - They're all part of what the task costs.

</details>

### Q5. How should you pick the budget value?

- A. As low as possible
- B. From eval data: well above normal runs (for example p95 x 2), so it only stops runaway ones
- C. The model's context window
- D. 1,000 tokens

<details><summary>Answer</summary>

**Answer: B** - A budget that stops good runs is a bug.

</details>
