---
type: quiz
title: "Quick check: worktree or clone"
minutes: 6
---

### Q1. Two agents must fix two unrelated bugs in the same repo at once on your laptop. Best setup?

- A. Both in the main checkout
- B. Two full clones
- C. One worktree per agent
- D. One agent after the other in /tmp

<details><summary>Answer</summary>

**Answer: C** - Worktrees isolate files and branches cheaply while sharing history.

</details>

### Q2. You need two copies of the same branch checked out at once. What works?

- A. Two worktrees on that branch
- B. A second clone (or a new branch for the second worktree)
- C. git worktree add --force twice
- D. claude -w twice with the same name

<details><summary>Answer</summary>

**Answer: B** - Git allows a branch to be checked out in only one worktree.

</details>

### Q3. Tests fail in a new worktree with `missing .env`. Why, and what fixes it for every future worktree?

- A. Worktrees are read-only; use a clone
- B. The branch is wrong; set baseRef
- C. A worktree is a fresh checkout of tracked files; list .env in .worktreeinclude
- D. Run /doctor

<details><summary>Answer</summary>

**Answer: C** - .worktreeinclude copies matching gitignored files into each new worktree.

</details>

### Q4. Inside a `claude -w fix-tax` session the agent runs `git -C ../.. commit -am wip`. What happens?

- A. It commits on main
- B. It commits on worktree-fix-tax
- C. Claude Code blocks it as a git redirect into the main checkout
- D. Git errors

<details><summary>Answer</summary>

**Answer: C** - Worktree isolation refuses git commands redirected at the main checkout.

</details>
