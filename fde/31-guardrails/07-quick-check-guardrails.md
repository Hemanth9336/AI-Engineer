---
type: quiz
title: "Quick check: guardrails"
minutes: 3
---

### Q1. Why enforce 'never promise refunds' in code as well as the prompt?

- A. Prompts are expensive
- B. Code is faster
- C. The model follows the prompt most of the time, and at scale the rest are real, binding promises
- D. Prompts can't contain rules

<details><summary>Answer</summary>

**Answer: C** - Important rules need a deterministic check.

</details>

### Q2. What's a cheap way to detect off-topic questions in a RAG bot?

- A. Ask a large model
- B. Block every question mark
- C. Count the words
- D. Use the best retrieval similarity score with a threshold chosen from real data

<details><summary>Answer</summary>

**Answer: D** - The retrieval embedding is already there.

</details>

### Q3. A retrieved article tells the model to ask for passwords. What kind of attack is this?

- A. Direct injection
- B. A jailbreak by the user
- C. SQL injection
- D. Indirect prompt injection

<details><summary>Answer</summary>

**Answer: D** - The attack arrives through content, not the user.

</details>

### Q4. Which mitigation limits damage even if an injection succeeds?

- A. A longer system prompt
- B. Higher temperature
- C. Least privilege: tools and outputs that can't do harm (no sending emails, output filters on contact details)
- D. A bigger model

<details><summary>Answer</summary>

**Answer: C** - What the model can't do, it can't be tricked into doing.

</details>
