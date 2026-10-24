---
type: quiz
title: "Quick check: stop conditions"
minutes: 4
---

### Q1. Why can the implicit stop - 'no tool calls means done' - end a task too early?

- A. Models never use tools
- B. The API forbids text replies
- C. Models sometimes reply with text mid-task, like 'Let me check the folder first'
- D. It uses too many tokens

<details><summary>Answer</summary>

**Answer: C** - A text reply might be thinking out loud. An explicit finish tool separates 'done' from 'talking'.

</details>

### Q2. Your agent's step limit is 8 and a run hits it. What should the exit status be?

- A. 0, because the program didn't crash
- B. It doesn't matter
- C. Non-zero, so callers can tell a limit hit from a real answer
- D. The number of steps taken

<details><summary>Answer</summary>

**Answer: C** - A stopped run did not complete the task. Make that visible to scripts and monitoring.

</details>

### Q3. Which labmock script models a runaway agent?

- A. ["Done."]
- B. [{"tool": "finish", "args": {"answer": "x"}}]
- C. []
- D. [{"tool": "list_dir", "args": {"path": "."}}]

<details><summary>Answer</summary>

**Answer: D** - labmock repeats the last step forever, so a script ending in a non-finish tool call never stops.

</details>

### Q4. A model ignores your 'call finish' nudge again and again. What should the harness do?

- A. Nudge forever
- B. Delete the history and start over
- C. Return the last text as if it were a final answer, silently
- D. Allow a small fixed number of nudges, then stop with a clear failure

<details><summary>Answer</summary>

**Answer: D** - Every loop in a harness - including the nudge loop - needs a bound.

</details>

### Q5. What's the best source for choosing a step limit?

- A. Traces of successful runs: set the limit comfortably above the normal range
- B. A round number like 100
- C. The model's context window size
- D. Whatever the provider recommends

<details><summary>Answer</summary>

**Answer: A** - Real step counts tell you how much room good runs need.

</details>
