---
type: quiz
title: "Quick check: hooks and rules"
minutes: 4
---

### Q1. A PreToolUse hook exits with code 2. What happens?

- A. The call runs with a warning
- B. Claude Code exits
- C. The call is blocked and the hook's stderr goes to the model as the reason
- D. The hook is retried

<details><summary>Answer</summary>

**Answer: C** - Exit 2 is the block signal.

</details>

### Q2. "Never deploy to production" must hold even if the model is confused or injected. Where does it go?

- A. CLAUDE.md
- B. A PreToolUse hook or a deny rule - enforcement, not a request
- C. The prompt
- D. A skill

<details><summary>Answer</summary>

**Answer: B** - Instructions are usually followed; hooks always run.

</details>

### Q3. Which belongs in CLAUDE.md?

- A. The exact test command and project conventions
- B. The API key for the test database
- C. A copy of the whole codebase
- D. Generic advice like 'write good code'

<details><summary>Answer</summary>

**Answer: A** - Specific, project-only, checkable.

</details>

### Q4. How do you show a CLAUDE.md rule actually changes behavior?

- A. Read it twice
- B. Put it in capital letters
- C. Make it longer
- D. Run the same task with and without it and compare what the agent did

<details><summary>Answer</summary>

**Answer: D** - Same method as any prompt change - before and after.

</details>

### Q5. Your hook script crashes on unexpected input (exit 1). What does Claude Code do with the call?

- A. Blocks it
- B. Asks the model
- C. Deletes the hook
- D. Treats it as a hook error and lets the call continue - so critical hooks should fail closed with exit 2

<details><summary>Answer</summary>

**Answer: D** - Only exit 2 blocks.

</details>
