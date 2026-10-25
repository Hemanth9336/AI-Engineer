---
type: quiz
title: "Quick check: what a plan run produces"
minutes: 9
---

### Q1. In plan mode, which of these can Claude do without your approval?

- A. Edit src/app.py
- B. Run npm install
- C. Run git diff and read files
- D. Commit the plan

<details><summary>Answer</summary>

**Answer: C** - Plan mode allows reads and read-only commands; edits and state changes wait for approval.

</details>

### Q2. What does `claude -p "..." --permission-mode plan --output-format json` give you?

- A. A diff of the changes it made
- B. An error - plan mode is interactive only
- C. An envelope whose result is the plan; the repo is unchanged
- D. A commit on a new branch

<details><summary>Answer</summary>

**Answer: C** - A headless plan run returns the plan as its result.

</details>

### Q3. Where does Claude keep the plan during a plan-mode session?

- A. In a file under ~/.claude/plans/
- B. In CLAUDE.md
- C. Only in the conversation
- D. In .git/PLAN

<details><summary>Answer</summary>

**Answer: A** - The plan file is the one file plan mode may write, and it is re-injected after compaction.

</details>

### Q4. While executing an approved plan, Claude finds the plan missed a required database migration. Best move?

- A. Let it improvise the migration
- B. Go back to planning and get the migration into a revised plan
- C. Skip the migration
- D. Switch to bypassPermissions

<details><summary>Answer</summary>

**Answer: B** - Unplanned work is exactly what the plan step exists to surface for review.

</details>
