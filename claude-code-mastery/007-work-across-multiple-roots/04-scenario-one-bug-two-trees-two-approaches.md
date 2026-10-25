---
type: scenario
title: "Scenario: one bug, two trees, two approaches"
minutes: 8
---

A pricing bug needs a fix in the `checkout` repo, and the fix depends on reading the pricing rules in the separate `pricing-rules` repo, which you must not change. Separately, a teammate asks you to try two different fixes for the checkout bug in parallel to compare them.

### Q1. How do you give the checkout session access to the pricing rules?

- A. claude --add-dir ../pricing-rules from inside checkout
- B. Start claude in the parent folder of both repos
- C. Copy the rules into checkout
- D. Add pricing-rules to .gitignore

<details><summary>Answer</summary>

**Answer: A** - An added root grants exactly that one extra folder for the session.

</details>

### Q2. Pricing-rules must stay unchanged. What else do you do?

- A. Nothing - added roots are read-only
- B. Run in a mode where edits prompt, or deny Edit for that path, and review the diff
- C. Delete the folder after the session
- D. Use --add-dir twice

<details><summary>Answer</summary>

**Answer: B** - Added roots follow the permission mode, so an edit-friendly mode could change them; deny or review edits there.

</details>

### Q3. For the two parallel fixes, what is the right tool?

- A. Two --add-dir flags
- B. One session with /clear between fixes
- C. Two git worktrees of checkout, one agent each
- D. A second clone made with cp -r

<details><summary>Answer</summary>

**Answer: C** - Worktrees give each attempt its own branch and working folder in the same repository.

</details>
