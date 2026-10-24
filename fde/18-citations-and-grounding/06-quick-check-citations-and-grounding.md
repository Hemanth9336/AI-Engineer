---
type: quiz
title: "Quick check: citations and grounding"
minutes: 4
---

### Q1. Why give the refusal an exact sentence?

- A. Code and evals can detect it reliably
- B. It's friendlier
- C. It's shorter
- D. The API needs it

<details><summary>Answer</summary>

**Answer: A** - Detectable refusals enable UI routing and measurement.

</details>

### Q2. A response cites [a7], but you only sent a1, a3 and a9. What is it?

- A. An invalid citation - flag or reject the answer
- B. Fine
- C. A better source
- D. A formatting issue only

<details><summary>Answer</summary>

**Answer: A** - Citations must reference the sources actually provided.

</details>

### Q3. How do you test grounding?

- A. Easy questions
- B. Longer prompts
- C. Trap questions: on-topic, plausible, and not answered by any document
- D. Higher temperature

<details><summary>Answer</summary>

**Answer: C** - Only uncovered questions reveal invented answers.

</details>

### Q4. Does a valid citation prove the fact is in the source?

- A. No - it shows where the model claims it came from; a faithfulness check compares the claim to the text
- B. Yes
- C. Only with JSON mode
- D. Only at temperature 0

<details><summary>Answer</summary>

**Answer: A** - Citations enable verification but aren't verification.

</details>
