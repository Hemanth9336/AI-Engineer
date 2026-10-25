---
type: quiz
title: "Quick check: Claude Code as a harness"
minutes: 6
---

### Q1. In `claude -p`, the model asks to run a Bash command that isn't covered by `--allowedTools`. What happens?

- A. It runs anyway
- B. Claude Code waits for input forever
- C. It's denied, the model gets an error result, and the result event lists it in permission_denials
- D. The run crashes

<details><summary>Answer</summary>

**Answer: C** - Non-interactive mode can't ask, so it denies and reports.

</details>

### Q2. Which stream-json event tells you how many turns a run took and what it cost?

- A. The init event
- B. The result event
- C. Every assistant event
- D. The first user event

<details><summary>Answer</summary>

**Answer: B** - `num_turns` and `total_cost_usd` are on the final result event.

</details>

### Q3. Which course topic does Claude Code's `Task` tool correspond to?

- A. Compaction
- B. Retrieval
- C. Subagents - a fresh context for a subtask
- D. Secrets hygiene

<details><summary>Answer</summary>

**Answer: C** - Same idea as your delegate tool in topic 25.

</details>

### Q4. Why pass `--max-turns` on every scripted `claude -p` run?

- A. It's required
- B. It makes the model smarter
- C. It's the step limit from topic 8 - a confused run can't loop forever
- D. It enables tools

<details><summary>Answer</summary>

**Answer: C** - Always cap automated runs.

</details>

### Q5. What is the main way production harnesses differ from your hand-built one?

- A. Depth: layered permissions, extension points, and handling of unhappy paths
- B. They use a different kind of loop
- C. They don't use tool calling
- D. They never need evals

<details><summary>Answer</summary>

**Answer: A** - Same building blocks, much more hardening.

</details>
