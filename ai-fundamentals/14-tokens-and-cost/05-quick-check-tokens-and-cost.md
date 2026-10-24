---
type: quiz
title: "Quick check: tokens and cost"
minutes: 4
---

### Q1. Which is usually more expensive per token?

- A. Output tokens
- B. Input tokens
- C. They are always the same
- D. Tokens in the system message

<details><summary>Answer</summary>

**Answer: A** - Generating tokens costs more than reading them; output is typically 3-5x the input price.

</details>

### Q2. Turn 30 of a chat has prompt_tokens = 18,000 even though the new question is one line. Why?

- A. prompt_tokens counts the whole history sent with the request, not just the new message
- B. The model is broken
- C. The provider overcharges
- D. max_tokens is too high

<details><summary>Answer</summary>

**Answer: A** - Every turn re-sends the history, and all of it counts as input.

</details>

### Q3. A request uses 1,000 input and 500 output tokens. Input costs $1 per 1M, output $5 per 1M. What does it cost?

- A. $0.0015
- B. $3.50
- C. $0.0060
- D. $0.0035

<details><summary>Answer</summary>

**Answer: D** - 1000 x 1/1e6 + 500 x 5/1e6 = 0.001 + 0.0025 = $0.0035.

</details>

### Q4. What usually saves the most money on a high-volume, simple task?

- A. A longer system prompt
- B. Using a smaller model tier that still passes your tests
- C. Raising the temperature
- D. Streaming the response

<details><summary>Answer</summary>

**Answer: B** - Model tier differences are often 20x or more - far larger than prompt tweaks.

</details>
