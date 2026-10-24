---
type: quiz
title: "Quick check: permission models"
minutes: 5
---

### Q1. Why is a denylist (block rm, sudo; allow everything else) a weak shell policy?

- A. It's slow
- B. It fails open: anything you didn't list, like find -delete or /bin/rm, gets through
- C. It's hard to write
- D. Models ignore it

<details><summary>Answer</summary>

**Answer: B** - An allowlist fails closed - unknown commands are asked about, not run.

</details>

### Q2. `cat README.md; rm -rf services` starts with an allowed program. What should happen?

- A. Allow - cat is allowed
- B. Deny - shell operators let one call run several commands
- C. Ask
- D. Run only the first part

<details><summary>Answer</summary>

**Answer: B** - Refuse operators outright; the agent can make separate calls.

</details>

### Q3. Why run allowed commands with shlex.split and no shell?

- A. It's faster
- B. So the string isn't interpreted again by a shell - no hidden expansion, chaining or redirection
- C. Shells aren't installed
- D. To get colors

<details><summary>Answer</summary>

**Answer: B** - What you checked is exactly what runs.

</details>

### Q4. Which change shrinks blast radius the most for a database tool?

- A. An approval prompt
- B. A read-only user on a replica, with tools scoped to one customer
- C. A longer system prompt
- D. Logging every query

<details><summary>Answer</summary>

**Answer: B** - Make the dangerous action impossible rather than asking a tired human to catch it.

</details>

### Q5. What should the model get back when a command is denied?

- A. Nothing
- B. The policy source code
- C. A fake success
- D. A clear error with the reason, so it can choose another way or ask the user

<details><summary>Answer</summary>

**Answer: D** - Silent failures cause retries; fake successes cause wrong answers.

</details>
