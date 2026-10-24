---
type: quiz
title: "Quick check: measuring RAG quality"
minutes: 4
---

### Q1. hit@3 is 0.70. What's true?

- A. Answers are 70% correct
- B. Faithfulness is 70%
- C. The prompt is wrong
- D. For 30% of questions the source never reaches the model, so those answers can only be guesses

<details><summary>Answer</summary>

**Answer: D** - hit@k caps answer quality.

</details>

### Q2. Which metric needs no expected answer?

- A. Correctness
- B. Faithfulness - it compares the answer to the sources
- C. hit@1
- D. Pass rate

<details><summary>Answer</summary>

**Answer: B** - So it can run on live traffic.

</details>

### Q3. A judge returns faithful: true and lists one unsupported claim. What should your code do?

- A. Treat it as unfaithful
- B. Trust 'true'
- C. Ignore the case
- D. Re-run until it agrees

<details><summary>Answer</summary>

**Answer: A** - Any unsupported claim means unfaithful.

</details>

### Q4. How should you present failures to a customer?

- A. Hide them
- B. Only in an appendix
- C. As one percentage
- D. Grouped into fixable now, needs the customer, and acceptable - with real examples

<details><summary>Answer</summary>

**Answer: D** - Buckets turn failures into a plan.

</details>
