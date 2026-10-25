---
type: scenario
title: "Scenario: starting agent work on an existing repo"
minutes: 9
---

You join a team and are asked to "use Claude Code to speed up" work on a five-year-old service with no tests for half its modules, a `.env` in the repo root, a `deploy.sh` that pushes to production, and no CLAUDE.md. Your first ticket is a small bug.

### Q1. What do you do before asking Claude to fix anything?

- A. Run with bypassPermissions to see what it does
- B. Explore read-only (or in plan mode) and write a short CLAUDE.md with the build and test commands
- C. Ask Claude to refactor the whole service first
- D. Delete .env

<details><summary>Answer</summary>

**Answer: B** - Understanding and standing instructions come first; they make every later run better.

</details>

### Q2. Which guardrails go in project settings on day one?

- A. allow Bash(*)
- B. None - CLAUDE.md is enough
- C. deny Read(./.env) and Bash(./deploy.sh *), ask for git push, allow the test command
- D. defaultMode bypassPermissions

<details><summary>Answer</summary>

**Answer: C** - Deny secrets and production-touching commands, keep pushes reviewed, and pre-approve the safe loop.

</details>

### Q3. The module with the bug has no tests. How do you work?

- A. Let the agent fix it and trust the result
- B. Ask for a bigger model
- C. Skip testing - it is a small bug
- D. Have the agent write a failing test that reproduces the bug first, then fix it

<details><summary>Answer</summary>

**Answer: D** - A reproducing test turns 'looks fixed' into evidence.

</details>

### Q4. The fix is ready. How does it land?

- A. git add -A && git push
- B. Let the agent push to main
- C. Review the diff and git status, stage the fix and test, conventional commit, push after review
- D. Email the diff

<details><summary>Answer</summary>

**Answer: C** - Commit exactly what you reviewed, with a message the team can trust.

</details>
