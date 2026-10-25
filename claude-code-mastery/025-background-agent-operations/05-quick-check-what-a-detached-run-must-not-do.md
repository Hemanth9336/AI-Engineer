---
type: quiz
title: "Quick check: what a detached run must not do"
minutes: 7
---

### Q1. Your background audit is in state `blocked` at 3am. What most likely happened?

- A. It finished
- B. It is compacting
- C. The model crashed
- D. It hit a permission prompt or asked a question and is waiting for you

<details><summary>Answer</summary>

**Answer: D** - blocked always means the session needs something from a person.

</details>

### Q2. Which instruction belongs in a background run's prompt?

- A. Ask me if anything is unclear
- B. Write artifacts/DONE as your very last action
- C. Push your branch to main when done
- D. Use any folder you like

<details><summary>Answer</summary>

**Answer: B** - A completion marker written last lets you tell finished runs from broken ones.

</details>

### Q3. How should a script read a background session's state?

- A. Parse ~/.claude/jobs/<id>/state.json
- B. ps aux | grep claude
- C. Grep the transcript
- D. claude agents --json --all

<details><summary>Answer</summary>

**Answer: D** - claude agents --json is the supported interface; the jobs files are internal.

</details>

### Q4. In a git repository, where does a claude --bg session make its edits?

- A. Directly on your checked-out branch
- B. In its own worktree under .claude/worktrees/
- C. In /tmp
- D. Nowhere - background sessions are read-only

<details><summary>Answer</summary>

**Answer: B** - Background sessions isolate their edits in a worktree unless isolation is turned off.

</details>
