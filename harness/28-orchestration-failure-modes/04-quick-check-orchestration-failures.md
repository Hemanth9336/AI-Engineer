---
type: quiz
title: "Quick check: orchestration failures"
minutes: 5
---

### Q1. A subagent restarted production even though the user said staging only. What's the most likely cause?

- A. Lost context: the handoff carried the task but not the user's constraint
- B. The subagent's model is bad
- C. The tool is broken
- D. Rate limits

<details><summary>Answer</summary>

**Answer: A** - The subagent only knows what it's given.

</details>

### Q2. Who should guarantee the original request reaches the subagent?

- A. The harness, by adding it to every brief
- B. The parent model, by writing good tasks
- C. The user, by repeating it
- D. The subagent, by asking

<details><summary>Answer</summary>

**Answer: A** - Don't rely on the model to never drop it.

</details>

### Q3. Two agents keep sending the same draft back and forth. What fixes it?

- A. A bigger model
- B. A longer system prompt
- C. More agents
- D. A retry cap and a single owner for the final decision

<details><summary>Answer</summary>

**Answer: D** - Ping-pong needs a stop condition and a decider.

</details>

### Q4. How do you prevent a ticket being opened twice by two subagents?

- A. Reports list side effects, the parent tracks them, and tools are idempotent (for example a dedupe key)
- B. Hope
- C. Run them sequentially always
- D. Disable tickets

<details><summary>Answer</summary>

**Answer: A** - Make actions visible and safe to repeat.

</details>

### Q5. What log makes lost-context bugs obvious?

- A. Only the final answers
- B. Token counts
- C. Each subagent's full first messages and its report, linked to the parent step
- D. The model version

<details><summary>Answer</summary>

**Answer: C** - You see exactly what the subagent was told.

</details>
