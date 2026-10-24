---
type: quiz
title: "Quick check: similarity"
minutes: 6
---

### Q1. What does a cosine similarity near 0 mean for two text embeddings?

- A. They are unrelated in meaning
- B. They are identical
- C. They are opposites
- D. One of them is empty

<details><summary>Answer</summary>

**Answer: A** - Near 0 means the vectors are at right angles - no shared meaning.

</details>

### Q2. cosine([1, 2], [2, 4]) is:

- A. 0.5
- B. 1.0
- C. 2.0
- D. 0

<details><summary>Answer</summary>

**Answer: B** - Same direction, different length - cosine ignores length.

</details>

### Q3. Why is cosine similarity the same as the dot product for lab-embed vectors?

- A. Because they have 384 dimensions
- B. It isn't
- C. Because they are positive
- D. Because the vectors are normalised to length 1

<details><summary>Answer</summary>

**Answer: D** - With length 1, the denominator is 1.

</details>

### Q4. Model X gives related pairs 0.85 and unrelated 0.70. Model Y gives 0.60 and 0.05. Which is worse at telling them apart?

- A. Neither - what matters is that related ranks above unrelated, and thresholds must be tuned per model
- B. X, the scores are higher
- C. Y, the scores are lower
- D. You can't compare

<details><summary>Answer</summary>

**Answer: A** - Absolute scores differ by model; ranking and per-model thresholds matter.

</details>
