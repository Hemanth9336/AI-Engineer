---
type: quiz
title: "Quick check: evals for agents"
minutes: 5
---

### Q1. Why isn't grading only the final answer enough for an agent?

- A. The agent takes actions; a right answer can come with dangerous, wasteful or wrong actions
- B. Answers are too short
- C. Final answers can't be graded
- D. Models don't produce final answers

<details><summary>Answer</summary>

**Answer: A** - Grade the trajectory and the resulting state too.

</details>

### Q2. Which is an outcome check?

- A. read_file was called
- B. notes/oncall.md contains 'Billing on-call: Priya' after the run
- C. At most 2 tool calls
- D. delete_file was never called

<details><summary>Answer</summary>

**Answer: B** - It looks at the end state, not the steps.

</details>

### Q3. What's the risk of a step check like 'must call list_dir then read_file'?

- A. It fails good agents that take a different, equally valid path
- B. None
- C. It's too slow
- D. It can't be automated

<details><summary>Answer</summary>

**Answer: A** - Step checks should encode real requirements - safety, cost - not one preferred path.

</details>

### Q4. Why run each eval task in a fresh copy of the workspace?

- A. To save disk
- B. To make it slower
- C. The agent requires it
- D. So tasks don't affect each other and the resulting state can be compared to the original

<details><summary>Answer</summary>

**Answer: D** - Isolation makes results repeatable and state checks meaningful.

</details>

### Q5. A task passed once. What should you report?

- A. A pass rate over several runs, because agent behavior varies
- B. That it passes
- C. Nothing
- D. The number of tokens

<details><summary>Answer</summary>

**Answer: A** - Agents are non-deterministic; one run hides rare failures.

</details>
