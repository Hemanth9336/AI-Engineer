---
type: quiz
title: "Quick check: file-based memory"
minutes: 4
---

### Q1. Why does an agent need files for memory?

- A. Files are faster than the model
- B. Models can't read long prompts
- C. The context window disappears when the run ends; files persist between runs
- D. To save tokens on the first call

<details><summary>Answer</summary>

**Answer: C** - Anything that must outlive the process has to be written somewhere durable.

</details>

### Q2. Which belongs in a long-lived notes file?

- A. The user decided the change window is Sunday 02:00-04:00
- B. The full contents of billing.yaml
- C. The current CPU usage
- D. The lab API key

<details><summary>Answer</summary>

**Answer: A** - Durable decisions and preferences. File contents and live status should be re-read; secrets never go in.

</details>

### Q3. When should a resumable harness save its checkpoint?

- A. Before each tool call
- B. Every 10 seconds
- C. Only at the end
- D. After every complete step - the assistant message and all its tool results

<details><summary>Answer</summary>

**Answer: D** - Saving between a tool call and its result would leave an invalid history.

</details>

### Q4. A task finishes but state.json is not deleted. What goes wrong?

- A. Nothing
- B. The model gets slower
- C. The notes file is erased
- D. The next --resume continues a task that's already done

<details><summary>Answer</summary>

**Answer: D** - Delete the checkpoint when the task completes.

</details>

### Q5. The agent crashed right after sending an email, before saving state. What protects you on resume?

- A. Idempotent side effects or a record of what was done, so it isn't sent twice
- B. Nothing can
- C. A bigger context window
- D. Restarting from scratch

<details><summary>Answer</summary>

**Answer: A** - Resume replays from the last checkpoint, so side effects since then may run again.

</details>
