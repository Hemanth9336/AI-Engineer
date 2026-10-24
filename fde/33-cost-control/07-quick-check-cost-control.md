---
type: quiz
title: "Quick check: cost control"
minutes: 3
---

### Q1. What must a response cache key include?

- A. Only the question
- B. The timestamp
- C. Everything that can change the answer: model, prompt, normalised question, and sources or user where relevant
- D. The user's IP

<details><summary>Answer</summary>

**Answer: C** - Otherwise stale or wrong answers get served.

</details>

### Q2. Which answer should not be cached across users?

- A. When is support open?
- B. What are your payment terms?
- C. How heavy can a pallet be?
- D. Where is order MER-55120?

<details><summary>Answer</summary>

**Answer: D** - Live, personal data.

</details>

### Q3. How do you prove routing didn't hurt quality?

- A. Ask users
- B. Run the golden set with and without routing and compare per slice
- C. Check the bill
- D. Use a bigger model

<details><summary>Answer</summary>

**Answer: B** - Same eval, sliced.

</details>

### Q4. When should a budget check run?

- A. After the call
- B. Only in development
- C. Once a month
- D. Before the call, with actual usage recorded after

<details><summary>Answer</summary>

**Answer: D** - Once sent, it's paid.

</details>
