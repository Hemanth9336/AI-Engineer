---
type: quiz
title: "Quick check: LLM as judge"
minutes: 4
---

### Q1. Why give the judge the expected answer?

- A. It's faster
- B. Otherwise it grades with its own knowledge, which may not match the customer's policy
- C. To make prompts longer
- D. The API requires it

<details><summary>Answer</summary>

**Answer: B** - The expected answer is the source of truth, not the judge.

</details>

### Q2. Why prefer pass/fail over a 1-10 score?

- A. Fewer tokens
- B. Scores are illegal
- C. Binary verdicts with reasons are more consistent and easier to act on
- D. Models can't count

<details><summary>Answer</summary>

**Answer: C** - Scales drift; verdicts don't.

</details>

### Q3. A friendly answer with a wrong deadline passes. Which pitfall is it?

- A. Self-preference
- B. Context overflow
- C. Temperature
- D. Politeness and leniency bias

<details><summary>Answer</summary>

**Answer: D** - Fix with 'grade facts only' and an explicit numbers rule.

</details>

### Q4. How do you know a judge is trustworthy?

- A. It uses the biggest model
- B. It gives long reasons
- C. Its verdicts agree with human labels on a sample, measured and re-measured after changes
- D. It passes most answers

<details><summary>Answer</summary>

**Answer: C** - Agreement with experts is the evidence.

</details>
