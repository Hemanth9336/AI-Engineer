---
type: quiz
title: "Quick check: how LLMs work"
minutes: 4
---

### Q1. What does an LLM compute at each step of generating an answer?

- A. The next sentence
- B. Probabilities for the next token, then one token is picked
- C. A database lookup
- D. The full answer at once

<details><summary>Answer</summary>

**Answer: B** - Generation is next-token prediction in a loop.

</details>

### Q2. A customer corrects the assistant's mistake in a chat. Tomorrow it makes the same mistake. Why?

- A. The model is broken
- B. Inference never changes the weights - the model doesn't learn from use
- C. The correction was too short
- D. The temperature was too high

<details><summary>Answer</summary>

**Answer: B** - Only training changes weights. Put corrected facts in the prompt instead.

</details>

### Q3. You ask the same factual question five times at temperature 1. The answer's key number changes every time. What does that suggest?

- A. The model is very creative
- B. Nothing
- C. The API is failing
- D. The model is likely inventing the fact

<details><summary>Answer</summary>

**Answer: D** - Stable knowledge tends to repeat; invented details vary.

</details>

### Q4. Which change most directly reduces hallucinations about a customer's internal policy?

- A. A bigger model
- B. A longer question
- C. Higher temperature
- D. Putting the policy text in the prompt and allowing 'I don't know'

<details><summary>Answer</summary>

**Answer: D** - The model can't know private facts - supply them and allow abstaining.

</details>
