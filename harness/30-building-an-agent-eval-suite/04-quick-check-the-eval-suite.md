---
type: quiz
title: "Quick check: the eval suite"
minutes: 6
---

### Q1. What makes a check 'objective'?

- A. A human agrees with it
- B. It uses a model
- C. Code can decide it, with no judgment: a string match, a file comparison, a count
- D. It's in JSON

<details><summary>Answer</summary>

**Answer: C** - Objective checks are cheap, repeatable and unambiguous.

</details>

### Q2. A file_contains check looks for text that the file already had. What's wrong?

- A. It passes even if the agent did nothing - it can't fail
- B. Nothing
- C. It's too strict
- D. It's a step check

<details><summary>Answer</summary>

**Answer: A** - A check that can't fail proves nothing.

</details>

### Q3. Why does the runner copy the workspace for each task?

- A. To be faster
- B. The agent needs a new folder name
- C. So one task's changes don't affect another, and the original can be compared
- D. To save tokens

<details><summary>Answer</summary>

**Answer: C** - Isolation and comparability.

</details>

### Q4. Production bug: the agent emailed a customer twice. What do you add to the suite?

- A. Nothing - it's fixed
- B. A golden task reproducing it, with a check that the email tool was called at most once
- C. A note in the README
- D. A bigger model

<details><summary>Answer</summary>

**Answer: B** - Every bug becomes a golden task, so it can't come back silently.

</details>

### Q5. Which task tests a must-never rule?

- A. 'Which port does billing use?' expecting 8081
- B. 'Create a note' expecting the file
- C. 'List services' with max 2 tool calls
- D. 'Clean up anything unused' expecting delete_file never called and README.md unchanged

<details><summary>Answer</summary>

**Answer: D** - It tempts the agent to do something it must not do.

</details>
