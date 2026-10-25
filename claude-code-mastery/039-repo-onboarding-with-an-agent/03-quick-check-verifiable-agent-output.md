---
type: quiz
title: "Quick check: verifiable agent output"
minutes: 11
---

### Q1. Which request produces onboarding output you can check with a script?

- A. Explain the architecture in a few paragraphs
- B. List every env var and its default as a table from app/config.py
- C. Describe the code style
- D. Summarize the team culture

<details><summary>Answer</summary>

**Answer: B** - A table of names and defaults can be compared to the config module line by line.

</details>

### Q2. The document says `make deploy`, and the Makefile has no deploy target. What does that tell you?

- A. The agent stated something it didn't read - fix the doc or the prompt
- B. The Makefile is out of date
- C. Make will create it
- D. Nothing

<details><summary>Answer</summary>

**Answer: A** - Invented commands are the classic failure of unverified generated docs.

</details>

### Q3. Why restrict the onboarding run to Read, Glob, Grep, and Write?

- A. It is faster
- B. Headless runs require it
- C. Glob needs it
- D. Exploration needs no shell or edits, and Write covers the single output file

<details><summary>Answer</summary>

**Answer: D** - Least privilege: the run can explore and write one document, nothing more.

</details>

### Q4. How do you keep ONBOARDING.md from going stale?

- A. Never change the code
- B. Mark it as draft
- C. Commit it, regenerate on change, and run the verification in CI
- D. Store it outside the repo

<details><summary>Answer</summary>

**Answer: C** - The checker that verified it once can keep verifying it.

</details>
