---
type: quiz
title: "Quick check: the fine-tuning decision"
minutes: 5
---

### Q1. A customer wants the model to 'know' their product catalogue, which changes weekly. Best approach?

- A. Fine-tune weekly
- B. A bigger model
- C. A longer system prompt
- D. RAG over the catalogue

<details><summary>Answer</summary>

**Answer: D** - Changing facts belong in retrieval.

</details>

### Q2. What is fine-tuning genuinely good at?

- A. Teaching new facts reliably
- B. Citing sources
- C. Enforcing permissions
- D. Consistent format or style and narrow, repeated tasks - often letting a smaller model do the job

<details><summary>Answer</summary>

**Answer: D** - Behaviour, not knowledge.

</details>

### Q3. In what order should you usually try the approaches?

- A. Fine-tune, RAG, prompt
- B. All at once
- C. Prompt, then RAG for knowledge, then fine-tune for a measured remaining gap
- D. RAG only

<details><summary>Answer</summary>

**Answer: C** - Cheapest and fastest first.

</details>

### Q4. How do you know a fine-tune helped?

- A. Lower training loss
- B. The provider says so
- C. It beats the baseline on the same golden set
- D. It feels better

<details><summary>Answer</summary>

**Answer: C** - Same eval, before and after.

</details>
