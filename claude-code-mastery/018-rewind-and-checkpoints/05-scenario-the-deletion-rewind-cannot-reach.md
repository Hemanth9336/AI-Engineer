---
type: scenario
title: "Scenario: the deletion rewind cannot reach"
minutes: 8
---

During a refactor, you asked Claude to "tidy up the scripts folder". It ran `git rm -r scripts/old` and `rm -rf scripts/tmp` through Bash, then edited `scripts/build.sh` with Edit. You press Esc Esc and choose Restore code at the prompt before the tidy-up.

### Q1. What comes back?

- A. Everything
- B. Nothing
- C. build.sh's edit is undone; scripts/old and scripts/tmp stay deleted
- D. Only scripts/tmp

<details><summary>Answer</summary>

**Answer: C** - Only the Edit was checkpointed; the Bash deletions were never tracked.

</details>

### Q2. scripts/old was tracked by git. How do you get it back?

- A. /rewind again
- B. git restore --staged --worktree scripts/old (or restore from the checkpoint tag)
- C. Ask Claude to recreate it from memory
- D. It is gone

<details><summary>Answer</summary>

**Answer: B** - git rm staged the deletion; restoring from HEAD or the tag brings the files back.

</details>

### Q3. scripts/tmp held untracked files. What does that mean?

- A. Neither /rewind nor git can restore them - only a backup could
- B. git can restore them
- C. They are in the trash
- D. Claude Code keeps a copy

<details><summary>Answer</summary>

**Answer: A** - Files git never tracked and Claude never edited have no snapshot anywhere.

</details>

### Q4. What would have prevented this?

- A. A bigger model
- B. A clean tree plus a checkpoint tag, and an ask rule for rm -rf
- C. Running /compact first
- D. Plan mode for the execution

<details><summary>Answer</summary>

**Answer: B** - A checkpoint makes tracked changes reversible; an ask rule stops destructive commands for review.

</details>
