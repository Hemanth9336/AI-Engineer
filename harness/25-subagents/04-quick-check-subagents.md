---
type: quiz
title: "Quick check: subagents"
minutes: 5
---

### Q1. What is the main benefit of a subagent?

- A. It works in a fresh context and returns only a short report, keeping the parent's context small
- B. It uses a bigger model
- C. It never makes mistakes
- D. It runs without tools

<details><summary>Answer</summary>

**Answer: A** - The reading happens in the subagent's context, not the parent's.

</details>

### Q2. What does a subagent know when it starts?

- A. Everything the parent has seen
- B. Only its system prompt and the task it was given
- C. The user's whole conversation
- D. The previous subagent's results

<details><summary>Answer</summary>

**Answer: B** - Which is why the brief must be self-contained.

</details>

### Q3. Why not give the subagent the delegate tool too?

- A. Subagents could spawn subagents without limit - recursion with no natural stop
- B. It's slower
- C. The API forbids it
- D. Subagents can't use tools

<details><summary>Answer</summary>

**Answer: A** - Keep the tree shallow unless you deliberately design for depth, with limits.

</details>

### Q4. Which report is most useful to the parent?

- A. The subagent's full message history
- B. Every file it read
- C. Just 'done'
- D. The answer, evidence pointers, actions taken and anything it couldn't do

<details><summary>Answer</summary>

**Answer: D** - Short, checkable, and honest about gaps.

</details>

### Q5. When is a subagent a poor choice?

- A. A one-line lookup the parent could do in one tool call
- B. Searching many large files
- C. Isolating untrusted content
- D. Running research in parallel

<details><summary>Answer</summary>

**Answer: A** - Each subagent costs at least one extra model call plus its own system prompt.

</details>
