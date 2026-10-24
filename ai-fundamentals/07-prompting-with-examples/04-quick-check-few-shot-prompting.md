---
type: quiz
title: "Quick check: few-shot prompting"
minutes: 6
---

### Q1. What is the difference between zero-shot and few-shot prompting?

- A. Zero-shot uses no model; few-shot uses a small model
- B. Zero-shot is free and few-shot is paid
- C. Few-shot means sending the prompt a few times
- D. Zero-shot gives only instructions; few-shot also includes worked examples of input and ideal output

<details><summary>Answer</summary>

**Answer: D** - Few-shot shows the model the pattern instead of only describing it.

</details>

### Q2. Over the API, what is the cleanest way to add a worked example?

- A. A user message with the example input followed by an assistant message with the ideal answer
- B. Put it in max_tokens
- C. Two system messages
- D. A separate request before the real one

<details><summary>Answer</summary>

**Answer: A** - Each example becomes an earlier turn of the conversation, so the model sees itself answering in the right format.

</details>

### Q3. All four of your examples are labelled `billing`. What risk does that create?

- A. The model leans toward billing even when another label fits
- B. None - more examples are always better
- C. The request will be rejected
- D. The model will refuse to answer

<details><summary>Answer</summary>

**Answer: A** - Models pick up unintended patterns. Cover each label and mix the order.

</details>

### Q4. One example answer is written `Outage.` while the others are lower-case words. What will likely happen?

- A. Nothing; the model ignores formatting
- B. The model will fix the typo
- C. The model may copy that style sometimes, breaking the script that reads the label
- D. The API returns an error

<details><summary>Answer</summary>

**Answer: C** - The model copies examples literally - including inconsistencies.

</details>
