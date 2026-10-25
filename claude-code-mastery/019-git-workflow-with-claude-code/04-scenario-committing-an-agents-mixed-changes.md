---
type: scenario
title: "Scenario: committing an agent's mixed changes"
minutes: 9
---

After an hour with Claude your working tree holds: a bug fix in `billing.py`, an unrelated rename across `utils/`, a debug `print` you forgot in `api.py`, and a new `.env.local` with a real key. You ask: "commit all of this".

### Q1. What is wrong with letting the agent run `git add -A && git commit`?

- A. Nothing
- B. The agent cannot run git add
- C. git add -A is slow
- D. It bundles unrelated changes, the debug print, and a secret into one commit

<details><summary>Answer</summary>

**Answer: D** - One commit would mix two changes, ship a debug line, and leak the key.

</details>

### Q2. What do you do with .env.local?

- A. Commit it and rotate later
- B. Let Claude encrypt it
- C. Rename it to .env
- D. Add it to .gitignore and never stage it; rotate the key if it was ever committed

<details><summary>Answer</summary>

**Answer: D** - Secrets stay out of git; anything that was committed must be treated as leaked.

</details>

### Q3. How should the remaining work be committed?

- A. One commit: chore: various
- B. Two commits - fix(billing) and refactor(utils) - staged separately (git add -p), debug print removed first
- C. Three commits including the print
- D. Squash everything later

<details><summary>Answer</summary>

**Answer: B** - Separate, conventional commits keep history reviewable and revertable.

</details>

### Q4. Which rule stops a future run from sweeping everything into a commit?

- A. allow Bash(git *)
- B. deny Bash(git add -A) and Bash(git commit -a *), and tell the agent to commit only what is staged
- C. defaultMode bypassPermissions
- D. A longer CLAUDE.md

<details><summary>Answer</summary>

**Answer: B** - Deny rules make the policy enforced, not just requested.

</details>
