---
type: quiz
title: "Quick check: the empty diff"
minutes: 11
---

### Q1. Your bot runs in a pre-commit job and the working tree is clean. What should it do?

- A. Print 'nothing to commit' and exit 0 without calling the model
- B. Ask Claude for a message anyway
- C. Exit 1
- D. Create an empty commit

<details><summary>Answer</summary>

**Answer: A** - No diff means no work: don't spend tokens or fail the job.

</details>

### Q2. Why run the bot with `--tools ""`?

- A. It is required with --json-schema
- B. It disables the model
- C. It makes output deterministic
- D. The diff on stdin is all it needs; with no tools it can't run commands or wander

<details><summary>Answer</summary>

**Answer: D** - Least privilege for a single-input job; StructuredOutput still works.

</details>

### Q3. The model returns `type: "feature"`. The schema has an enum. Who should stop it from being committed?

- A. Your validator: it checks the enum again and exits 1
- B. Nobody, it is close enough
- C. git
- D. The changelog

<details><summary>Answer</summary>

**Answer: A** - Schemas guide the model; code you own enforces.

</details>

### Q4. apply.py fails after `git add -A`. What should the bot leave behind?

- A. A staged index
- B. Exactly the tree it found: unstage with git reset -q, exit 1
- C. A partial commit
- D. A deleted CHANGELOG

<details><summary>Answer</summary>

**Answer: B** - Atomic: either a valid commit, or nothing changed.

</details>
