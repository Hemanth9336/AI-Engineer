---
type: quiz
title: "Quick check: tokens, context, and cost"
minutes: 3
---

### Q1. Which text usually uses the most tokens per character?

- A. Plain English prose
- B. A single common word
- C. Order IDs, timestamps and codes
- D. Spaces

<details><summary>Answer</summary>

**Answer: C** - Rare strings split into many small tokens.

</details>

### Q2. Your request is rejected with 'context window exceeded'. What is the right fix?

- A. Retry the same request
- B. Shrink the prompt - fewer chunks, trimmed history, or a summary - then retry
- C. Raise max_tokens
- D. Switch to temperature 0

<details><summary>Answer</summary>

**Answer: B** - The prompt plus answer must fit; reduce what you send.

</details>

### Q3. A request uses 4,000 input and 500 output tokens. Prices: $0.50 / $2.00 per million. What does it cost?

- A. $0.0250
- B. $0.0045
- C. $0.0020
- D. $0.0030

<details><summary>Answer</summary>

**Answer: D** - 4,000/1M x 0.50 = 0.002; 500/1M x 2.00 = 0.001; total $0.003.

</details>

### Q4. Why does a long system prompt matter for cost?

- A. It's sent on every request, so its tokens are paid every time
- B. It doesn't
- C. It is only charged once
- D. It is charged as output

<details><summary>Answer</summary>

**Answer: A** - Fixed prompt tokens multiply by request volume.

</details>
