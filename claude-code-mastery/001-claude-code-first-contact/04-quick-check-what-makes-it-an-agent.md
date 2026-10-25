---
type: quiz
title: "Quick check: what makes it an agent"
minutes: 9
---

### Q1. What separates Claude Code from a chatbot answering the same request?

- A. It only answers questions about code
- B. It uses a larger model than chat products
- C. It acts in a loop - reading files, running tools, and checking results - until the goal is met
- D. It never asks you anything once started

<details><summary>Answer</summary>

**Answer: C** - The loop of read, act, check is what makes it an agent; a chatbot stops after one answer.

</details>

### Q2. Out of the box, which of these asks for your approval before it runs?

- A. Reading a file in the working folder
- B. Searching for a function name
- C. Listing the tools it has
- D. Editing a file or running a shell command that changes something

<details><summary>Answer</summary>

**Answer: D** - Reads are free; anything that changes files or the machine asks first until you allow it.

</details>

### Q3. The agent wrote `notes.md`, then you typed `/exit`. What happened to `notes.md`?

- A. It stays on disk - the conversation is temporary, the artifacts are real
- B. It was deleted with the conversation
- C. It moved into ~/.claude
- D. It is kept only if you ran /save

<details><summary>Answer</summary>

**Answer: A** - Leaving the console ends the conversation; files the agent created stay where it wrote them.

</details>

### Q4. Where does the reply of `claude -p "..." > answer.txt` end up?

- A. Only in the terminal
- B. In ~/.claude/answer.txt
- C. Nowhere - -p runs silently
- D. In answer.txt, because -p prints the reply to stdout

<details><summary>Answer</summary>

**Answer: D** - Headless mode prints the result on stdout, so shell redirection captures it like any command's output.

</details>
