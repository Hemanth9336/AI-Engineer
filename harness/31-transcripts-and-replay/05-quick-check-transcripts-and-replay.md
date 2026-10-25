---
type: quiz
title: "Quick check: transcripts and replay"
minutes: 4
---

### Q1. Why record full tool results in the transcript?

- A. They're small
- B. The API requires it
- C. Most agent bugs are in what the model saw, and you can't see that without them
- D. For billing

<details><summary>Answer</summary>

**Answer: C** - The result is the model's view of the world.

</details>

### Q2. What is the run ID for?

- A. Billing
- B. Encrypting the file
- C. Sorting alphabetically
- D. Tying together every event of one run, even when several runs or subagents log at once

<details><summary>Answer</summary>

**Answer: D** - Without it, interleaved logs are unreadable.

</details>

### Q3. A run answered wrong at step 4. Where do you start looking for the cause?

- A. Only at step 4
- B. At the system prompt only
- C. Walk back through the steps to find the first one where the information or decision went wrong
- D. At the token counts

<details><summary>Answer</summary>

**Answer: C** - The final answer is a consequence; the fix goes at the first wrong turn.

</details>

### Q4. The model guessed a port after reading a config file whose port line had been cut off. Which category?

- A. model_reasoning
- B. tool_description
- C. prompt
- D. tool_result

<details><summary>Answer</summary>

**Answer: D** - The model was starved of the information - the tool result is at fault.

</details>

### Q5. What does replaying from a transcript let you do?

- A. Undo actions
- B. Delete the transcript
- C. Rebuild the history to step N, change one thing and rerun from there - a reproducible experiment
- D. Train the model

<details><summary>Answer</summary>

**Answer: C** - It turns a one-off production failure into something you can test.

</details>
