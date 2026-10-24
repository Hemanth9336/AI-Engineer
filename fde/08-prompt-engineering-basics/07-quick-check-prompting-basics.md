---
type: quiz
title: "Quick check: prompting basics"
minutes: 3
---

### Q1. Which change most improves a vague 'Summarize this ticket' prompt?

- A. Adding 'you are a world-class expert'
- B. Writing it in capitals
- C. Raising temperature
- D. Stating the audience, the exact output lines and the allowed values

<details><summary>Answer</summary>

**Answer: D** - Specificity removes guesses.

</details>

### Q2. How do you add few-shot examples with a chat API?

- A. In the model name
- B. In max_tokens
- C. As a separate API call
- D. As user/assistant message pairs before the real input

<details><summary>Answer</summary>

**Answer: D** - Fake turns show the pattern directly.

</details>

### Q3. Why wrap a ticket in <ticket> tags?

- A. It marks the data so the model doesn't confuse it with instructions
- B. It is required by the API
- C. It reduces cost
- D. It changes the model

<details><summary>Answer</summary>

**Answer: A** - Clear boundaries between instructions and data.

</details>

### Q4. Your format check fails on one reply in 200. What should the code do?

- A. Pass it downstream anyway
- B. Handle it explicitly: retry, use a default, or flag for a human
- C. Crash the whole pipeline
- D. Remove the check

<details><summary>Answer</summary>

**Answer: B** - Every format has a failure path; decide it on purpose.

</details>
