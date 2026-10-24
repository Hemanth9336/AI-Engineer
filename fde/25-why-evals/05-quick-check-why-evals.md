---
type: quiz
title: "Quick check: why evals"
minutes: 4
---

### Q1. Why can't a five-question demo show a system works?

- A. The sample is tiny and hand-picked, so it can't represent the range of real questions
- B. Five is an unlucky number
- C. Demos are always rigged
- D. Models need warming up

<details><summary>Answer</summary>

**Answer: A** - Small, friendly samples hide failure rates.

</details>

### Q2. What three properties make an eval useful?

- A. Fixed questions, fixed scoring, and readable failures
- B. Speed, cost, color
- C. A big model, a long prompt, a GPU
- D. Random questions, human grading, one run

<details><summary>Answer</summary>

**Answer: A** - Comparable, repeatable, actionable.

</details>

### Q3. Why write the eval set with the customer?

- A. It becomes the shared definition of 'working' - scope, correctness and the bar are agreed upfront
- B. To save time
- C. Customers like typing
- D. It's required by law

<details><summary>Answer</summary>

**Answer: A** - The eval set is the spec.

</details>

### Q4. A user reports a wrong answer. What should happen to it?

- A. Ignore it
- B. Retrain the model
- C. It becomes a new eval case, so the fix is proven and can't silently regress
- D. Delete the log

<details><summary>Answer</summary>

**Answer: C** - Every complaint is a test case.

</details>
