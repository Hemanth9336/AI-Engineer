---
type: quiz
title: "Quick check: rewind boundaries"
minutes: 8
---

### Q1. Claude ran `sed -i 's/v1/v2/' config.yaml` through Bash; it never used Edit on that file. Will /rewind restore it?

- A. Yes
- B. Only after /compact
- C. Only in plan mode
- D. No - files changed only by Bash are not tracked

<details><summary>Answer</summary>

**Answer: D** - Checkpoints track Claude's file-editing tools; a Bash-only change needs version control.

</details>

### Q2. Which change can /rewind undo?

- A. A database migration the agent ran
- B. An Edit Claude made to src/app.py three prompts ago
- C. A git push
- D. A file a subagent wrote

<details><summary>Answer</summary>

**Answer: B** - Edits through Claude's file tools in your session are what checkpoints capture.

</details>

### Q3. You want to undo the agent's work but keep the file it wrote to notes/ideas.md. What do you run?

- A. git reset --hard && git clean -fd
- B. git push --force
- C. Copy notes/ideas.md aside (or exclude it from clean), then reset to the checkpoint
- D. /rewind twice

<details><summary>Answer</summary>

**Answer: C** - reset and clean remove everything since the checkpoint, so protect what you want to keep first.

</details>

### Q4. Why tag before the run instead of just remembering the commit?

- A. Tags make the agent faster
- B. Tags are pushed automatically
- C. git reset needs a tag
- D. A named checkpoint is unambiguous to restore to, even after new commits

<details><summary>Answer</summary>

**Answer: D** - A tag names the exact state you trust, whatever happens afterwards.

</details>
