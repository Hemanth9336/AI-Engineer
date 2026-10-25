---
type: quiz
title: "Quick check: /clear vs /compact"
minutes: 3
---

### Q1. You committed a feature and are starting an unrelated bug fix. Which command?

- A. /init
- B. /compact
- C. /clear
- D. /model

<details><summary>Answer</summary>

**Answer: C** - Different task: start fresh.

</details>

### Q2. Mid-refactor, the session is slow and the window is nearly full, but Claude needs the decisions made so far. Which command?

- A. /exit and start over
- B. /clear
- C. /compact with instructions to keep those decisions
- D. Nothing

<details><summary>Answer</summary>

**Answer: C** - Same task: summarize, don't erase.

</details>

### Q3. After /clear, what does Claude still know about the project?

- A. The last five messages
- B. Everything from the conversation
- C. Nothing at all
- D. What's in CLAUDE.md (and the system prompt)

<details><summary>Answer</summary>

**Answer: D** - Memory files are reloaded; the conversation is gone.

</details>

### Q4. Which usually fills the context window fastest?

- A. Your short prompts
- B. Tool results such as big files and long command output
- C. CLAUDE.md
- D. Slash commands

<details><summary>Answer</summary>

**Answer: B** - Outputs and file contents are the heavy part.

</details>

### Q5. How do you see what's using the context window?

- A. /context
- B. /clear
- C. /permissions
- D. claude --version

<details><summary>Answer</summary>

**Answer: A** - It breaks down the window by category.

</details>
