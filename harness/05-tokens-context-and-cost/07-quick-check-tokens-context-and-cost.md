---
type: quiz
title: "Quick check: tokens, context, and cost"
minutes: 3
---

### Q1. Your agent's step 7 shows prompt_tokens of 31,000 while step 1 had 900. What is the most likely reason?

- A. The model got slower
- B. Output tokens are counted as input
- C. The tokenizer changed between steps
- D. Every step re-sends the growing history, including earlier tool results

<details><summary>Answer</summary>

**Answer: D** - Each call carries the system prompt, tool definitions and the whole history so far. Large tool results keep being paid for on every later step.

</details>

### Q2. An agent request fails with 'context window exceeded' at step 12. What is the right kind of fix?

- A. Retry the same request
- B. Lower the temperature
- C. Raise max_tokens
- D. Shrink what the harness sends: trim tool results, compact old history, or move notes to a file

<details><summary>Answer</summary>

**Answer: D** - The prompt plus answer must fit the window. Retrying sends the same oversized prompt; the harness has to send less.

</details>

### Q3. A task takes 3 steps of 2,000, 3,000 and 4,000 input tokens and 100 output tokens each. Prices: $0.50 input, $2.00 output per million. What does the task cost?

- A. $0.0039
- B. $0.0045
- C. $0.0060
- D. $0.0051

<details><summary>Answer</summary>

**Answer: D** - Input 9,000 / 1M x 0.50 = $0.0045. Output 300 / 1M x 2.00 = $0.0006. Total $0.0051.

</details>

### Q4. Why does a long list of tool definitions matter for cost?

- A. Tools are free because they are not text
- B. Tool definitions are sent with every request, so their tokens are paid on every step
- C. Tool definitions are only charged once per conversation
- D. They are charged as output tokens

<details><summary>Answer</summary>

**Answer: B** - Definitions are part of the prompt. Twenty verbose tools can add thousands of tokens to every step.

</details>

### Q5. Where is the authoritative token count for a request?

- A. The usage field in the API response
- B. A word count divided by 0.75
- C. The length of the prompt in characters
- D. The model's documentation page

<details><summary>Answer</summary>

**Answer: A** - Estimates are useful, but usage is what you're billed for - read it on every step.

</details>
