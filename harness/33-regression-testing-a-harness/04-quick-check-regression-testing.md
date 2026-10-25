---
type: quiz
title: "Quick check: regression testing"
minutes: 4
---

### Q1. A teammate shortened the system prompt. How do you know it's safe?

- A. It reads better
- B. Run the eval suite before and after and compare per task
- C. Ask the model
- D. Check the token count

<details><summary>Answer</summary>

**Answer: B** - Prompt changes are behavior changes.

</details>

### Q2. Both versions score 5/6. Can you ship?

- A. Not without checking per task: one task may have broken and another been fixed
- B. Yes, same score
- C. Only on Fridays
- D. Only with a bigger model

<details><summary>Answer</summary>

**Answer: A** - Equal scores can hide a regression on your most important task.

</details>

### Q3. What is a regression in an eval suite?

- A. A task that's slow
- B. A new task
- C. A task that always fails
- D. A task that passed before the change and fails after it

<details><summary>Answer</summary>

**Answer: D** - Passed then, fails now.

</details>

### Q4. Why mark some tasks as must-pass?

- A. They're easy
- B. Safety rules shouldn't be traded for score elsewhere - one failure blocks the change
- C. They're slow
- D. To raise the score

<details><summary>Answer</summary>

**Answer: B** - Some failures are unacceptable regardless of the average.

</details>

### Q5. Why score the candidate over the baseline's task ids?

- A. It's faster
- B. To ignore new tasks
- C. The candidate has no ids
- D. So deleting a failing task from the suite can't make a change look better

<details><summary>Answer</summary>

**Answer: D** - A missing task counts as failed.

</details>
