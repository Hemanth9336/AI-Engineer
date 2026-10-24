---
type: quiz
title: "Quick check: reducing hallucinations"
minutes: 4
---

### Q1. Why skip the model call when no source clears the threshold?

- A. With nothing relevant to answer from, the model can only guess - refusing directly is cheaper and can't hallucinate
- B. To save tokens only
- C. Models need sources to start
- D. It's required

<details><summary>Answer</summary>

**Answer: A** - No sources, no call.

</details>

### Q2. Which is a useful confidence signal?

- A. The model's self-reported confidence
- B. Answer length
- C. The best retrieval score and citation validity
- D. Response time

<details><summary>Answer</summary>

**Answer: C** - System signals beat self-reported confidence.

</details>

### Q3. You raise the threshold and the trap abstain rate goes from 80% to 100%. What else must you check?

- A. Nothing
- B. The temperature
- C. Token count
- D. The false-abstain rate on answerable questions

<details><summary>Answer</summary>

**Answer: D** - Stricter means more refusals of real questions too.

</details>

### Q4. How should a refusal reach the user?

- A. As an error page
- B. With a next step - contact support, help centre link or handoff to a person
- C. Hidden
- D. Retried until it answers

<details><summary>Answer</summary>

**Answer: B** - A useful refusal routes the user.

</details>
