---
type: quiz
title: "Quick check: context budgeting"
minutes: 4
---

### Q1. In a typical agent trace at step 6, which part is usually the biggest?

- A. The system prompt
- B. Tool definitions
- C. Tool results in the history
- D. The user's question

<details><summary>Answer</summary>

**Answer: C** - Files, logs and listings pile up in the history and are re-sent every step.

</details>

### Q2. How do you measure the tokens a set of tool definitions adds?

- A. Count the words in the descriptions
- B. Divide the JSON length by 10
- C. Ask the model
- D. Compare usage.prompt_tokens of the same request with and without the tools, using max_tokens=1

<details><summary>Answer</summary>

**Answer: D** - Measuring by difference with the authoritative count is cheap and accurate enough.

</details>

### Q3. Your budget enforcer drops 'the oldest 4 messages'. What can go wrong?

- A. Nothing
- B. It's too slow
- C. It can split an assistant tool call from its results, making the history invalid
- D. It changes the system prompt

<details><summary>Answer</summary>

**Answer: C** - Drop whole turns - an assistant message with all of its tool results.

</details>

### Q4. Why add a note like '[note: 3 earlier steps were dropped...]'?

- A. The API requires it
- B. It reduces tokens
- C. So the model knows its history was shortened and doesn't assume it never looked at anything
- D. To confuse attackers

<details><summary>Answer</summary>

**Answer: C** - Without it, the model may silently repeat work or contradict what it found earlier.

</details>

### Q5. Which two messages should a budget enforcer never drop?

- A. The first two tool results
- B. The system prompt and the user's original task
- C. The longest messages
- D. Any assistant messages

<details><summary>Answer</summary>

**Answer: B** - They define the goal and the rules. Without them the agent drifts.

</details>
