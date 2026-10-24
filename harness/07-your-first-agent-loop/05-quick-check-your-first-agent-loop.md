---
type: quiz
title: "Quick check: your first agent loop"
minutes: 4
---

### Q1. In a minimal agent loop, what ends the loop?

- A. A fixed number of iterations
- B. A reply with no tool calls
- C. The user pressing Enter
- D. The first tool error

<details><summary>Answer</summary>

**Answer: B** - The model signals it's finished by answering in text instead of asking for a tool. (You'll add a hard limit next topic.)

</details>

### Q2. Your agent answers 'Billing uses port 9200' - wrong. The trace shows step 3 read services/search.yaml. Where is the bug?

- A. The model's arithmetic
- B. The tokenizer
- C. It read the wrong file - fix what it looks at (tool descriptions, listing, prompt)
- D. max_tokens was too low

<details><summary>Answer</summary>

**Answer: C** - The answer matches what it read. The failure is in which file it chose, so fix the information and guidance it gets.

</details>

### Q3. Why is a trace written as JSONL, one line per step?

- A. It's required by the API
- B. Lines can be appended as the loop runs and survive a crash halfway through
- C. JSONL is smaller than JSON
- D. Models can only read JSONL

<details><summary>Answer</summary>

**Answer: B** - Appending one line per step is cheap and crash-safe, and each line loads independently.

</details>

### Q4. prompt_tokens rises from 400 at step 1 to 1,500 at step 5. Why?

- A. The model is getting tired
- B. The system prompt is re-written each step
- C. Each request re-sends the whole history, which grows by an assistant message and tool results every step
- D. Token prices went up

<details><summary>Answer</summary>

**Answer: C** - The history only grows. That's why long loops get expensive - and why later topics trim and compact it.

</details>

### Q5. What is the biggest risk of `while True:` in an agent loop?

- A. A confused model can keep calling tools forever, burning tokens
- B. It's slow to write
- C. Python doesn't support it
- D. It prevents tool calls

<details><summary>Answer</summary>

**Answer: A** - The loop trusts the model to stop. A harness must not - add a step limit (topic 08).

</details>
