---
type: quiz
title: "Quick check: roles and framing"
minutes: 5
---

### Q1. What does 'You are a senior security engineer' in a system message mainly change?

- A. It gives the model new security knowledge it did not have
- B. It reduces the token cost
- C. It makes every answer correct
- D. It focuses the answer on what a security engineer would care about, in their style

<details><summary>Answer</summary>

**Answer: D** - A role selects a perspective and tone. It adds no new knowledge and no guarantee of accuracy.

</details>

### Q2. You must explain an outage to customers and to the on-call team. What should differ between the two prompts?

- A. The facts of the outage
- B. Only the model
- C. Nothing
- D. The audience and tone, while the facts stay the same

<details><summary>Answer</summary>

**Answer: D** - Audience and tone change the wording and detail; the facts must not change.

</details>

### Q3. A rewrite for executives keeps saying 'p99 latency'. What is the most direct fix?

- A. Use a bigger model
- B. Ask explicitly for no jargon and name the term to translate, e.g. 'say slow responses, not p99 latency'
- C. Lower max_tokens
- D. Remove the system message

<details><summary>Answer</summary>

**Answer: B** - Models echo the vocabulary they are given. Name the words to avoid and what to say instead.

</details>

### Q4. Where should the role usually go?

- A. In the final user message only
- B. In the system message
- C. In the assistant message
- D. In the request URL

<details><summary>Answer</summary>

**Answer: B** - The role applies to the whole conversation, so it belongs in the system message.

</details>
