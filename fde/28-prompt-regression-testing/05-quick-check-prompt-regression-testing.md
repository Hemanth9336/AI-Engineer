---
type: quiz
title: "Quick check: prompt regression testing"
minutes: 4
---

### Q1. You shorten a prompt and the score stays 5/6. Is it safe to ship?

- A. Not necessarily - check case by case; one case may be fixed and another broken
- B. Yes
- C. Only on Fridays
- D. Only with a bigger model

<details><summary>Answer</summary>

**Answer: A** - Same score can hide a swap.

</details>

### Q2. Why save results to a file per prompt version?

- A. So any two runs can be compared later, and the history is visible
- B. Disk is cheap
- C. The API requires it
- D. To slow things down

<details><summary>Answer</summary>

**Answer: A** - Saved runs make comparison and auditing possible.

</details>

### Q3. What threshold suits the trap (refusal) slice?

- A. 10% drop
- B. Whatever the customer forgets
- C. Zero - any regression fails
- D. No gate

<details><summary>Answer</summary>

**Answer: C** - Safety slices get no tolerance.

</details>

### Q4. Your scores wobble between identical runs. What helps?

- A. Run each case a few times and count it as passing only if it passes every time; allow a small max-drop
- B. Ignore evals
- C. Raise temperature
- D. Delete flaky cases

<details><summary>Answer</summary>

**Answer: A** - Handle noise explicitly.

</details>
