---
type: quiz
title: "Quick check: working across a codebase"
minutes: 5
---

### Q1. How does Claude Code get to know a large repository?

- A. It needs you to paste the code
- B. It loads every file into context at the start
- C. It searches and reads the relevant files as needed
- D. It only sees files you open with @

<details><summary>Answer</summary>

**Answer: C** - Selective exploration keeps the context window usable.

</details>

### Q2. Why say "definition, imports, calls and tests" when asking for a rename?

- A. It tells Claude what "everywhere" covers, so indirect uses like module.func() aren't missed
- B. It's required syntax
- C. It makes Claude use a different model
- D. It disables the tests

<details><summary>Answer</summary>

**Answer: A** - Explicit scope prevents half-done renames.

</details>

### Q3. Which is the quickest sanity check after a 12-file rename?

- A. `git diff --stat`, a grep for the old name, and the test suite
- B. Ask Claude if it's done
- C. Open each file in an editor
- D. Run the app once

<details><summary>Answer</summary>

**Answer: A** - Shape of the diff, nothing left behind, tests green.

</details>

### Q4. Claude is searching `node_modules/` for your business logic. What do you do?

- A. Restart the session
- B. Let it finish
- C. Delete node_modules
- D. Interrupt and point it to the right folder - and add a map to CLAUDE.md

<details><summary>Answer</summary>

**Answer: D** - Steer early; record the map so it doesn't happen again.

</details>

### Q5. What does an Explore subagent give you on a broad search?

- A. Write access to more files
- B. Faster typing
- C. Just the findings, without filling your main context with every file it read
- D. A copy of the repository

<details><summary>Answer</summary>

**Answer: C** - It searches in its own context and reports back.

</details>
