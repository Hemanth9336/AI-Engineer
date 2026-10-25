---
type: quiz
title: "Quick check: git work with Claude"
minutes: 5
---

### Q1. Which commit subject follows Conventional Commits?

- A. Fixed some stuff
- B. fix: round invoice totals half up
- C. WIP
- D. fix - rounding (final final)

<details><summary>Answer</summary>

**Answer: B** - `type: short imperative summary`.

</details>

### Q2. Which git command is safe to allow without asking in most projects?

- A. `git diff`
- B. `git push --force`
- C. `git reset --hard`
- D. `git push origin main`

<details><summary>Answer</summary>

**Answer: A** - Read-only commands are safe; history-rewriting ones aren't.

</details>

### Q3. A headless job should commit the generated changelog but never push. Which flags?

- A. `--allowedTools "Bash(git add:*)" "Bash(git commit:*)"`
- B. `--permission-mode bypassPermissions`
- C. `--allowedTools "Bash(git:*)"`
- D. No flags - headless runs can't use git

<details><summary>Answer</summary>

**Answer: A** - Grant exactly add and commit; push stays denied.

</details>

### Q4. Claude wrote a great commit message. What must you still check?

- A. That it used the word feat
- B. Nothing
- C. The spelling
- D. The diff and the list of staged files - the message describes the change, the diff is the change

<details><summary>Answer</summary>

**Answer: D** - Review the change itself.

</details>

### Q5. What's the safest way for Claude's change to reach main?

- A. Push straight to main
- B. A branch and a pull request that a human reviews
- C. Force-push
- D. Email the diff

<details><summary>Answer</summary>

**Answer: B** - PRs keep a human in the loop.

</details>
