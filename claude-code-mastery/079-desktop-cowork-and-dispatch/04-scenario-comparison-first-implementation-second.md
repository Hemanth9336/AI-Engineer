---
type: scenario
title: "Scenario: comparison first, implementation second"
minutes: 9
---

You must choose between two caching libraries for a service, then implement the winner. You want Claude to prototype both, compare them with numbers, and only then implement one. You'd like to do it in Desktop.

### Q1. How do you prototype both without the attempts colliding?

- A. One session doing both in turn
- B. Cowork
- C. Two sessions in the same folder
- D. Two sessions with the Worktree toggle on, one per library, each on its own branch

<details><summary>Answer</summary>

**Answer: D** - Worktrees give parallel sessions separate checkouts and branches.

</details>

### Q2. Which mode do you start each prototype session in?

- A. Bypass
- B. Plan, to agree on the approach and the benchmark first, then Accept edits for the prototype
- C. Auto with no plan
- D. Manual forever

<details><summary>Answer</summary>

**Answer: B** - Plan first keeps the comparison fair; then let it build.

</details>

### Q3. How do you review the two prototypes' changes?

- A. Read the chat summaries
- B. The diff pane in each session, with line comments, plus /code-review on each branch
- C. git log only
- D. Ask Dispatch

<details><summary>Answer</summary>

**Answer: B** - Visual review is where Desktop shines.

</details>

### Q4. The winner is chosen. What happens to the losing worktree?

- A. Delete the repo
- B. Archive that session after noting the results; its worktree is cleaned up later, so commit anything worth keeping first
- C. Merge both
- D. Leave it running

<details><summary>Answer</summary>

**Answer: B** - Uncommitted work in a worktree goes away with it.

</details>
