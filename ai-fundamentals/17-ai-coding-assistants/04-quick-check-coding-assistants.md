---
type: quiz
title: "Quick check: coding assistants"
minutes: 6
---

### Q1. Which task is a coding assistant most reliable at?

- A. Writing a small, well-specified script you can test
- B. Designing a company's whole architecture from one sentence
- C. Knowing your team's unwritten conventions
- D. Guaranteeing code has no bugs

<details><summary>Answer</summary>

**Answer: A** - Small, clear tasks with a way to verify them are where assistants shine.

</details>

### Q2. You pipe claude -p into a file and get a summary instead of code, and a new file appeared. Why?

- A. The model is broken
- B. The agent used its file-writing tool; use --tools "" to make it print the code
- C. max_tokens was too low
- D. The gateway rewrote the reply

<details><summary>Answer</summary>

**Answer: B** - With tools enabled, Claude Code may act instead of answering in text.

</details>

### Q3. What should you do before running an AI-generated script that deletes old files?

- A. Run it on production first
- B. Read it, check the paths and conditions, and try it on a safe copy
- C. Ask the model if it is safe and trust the answer
- D. Run it with sudo to avoid errors

<details><summary>Answer</summary>

**Answer: B** - You own the code. Read it and test it on harmless data first.

</details>

### Q4. What is CLAUDE.md for?

- A. Storing your API key
- B. Listing MCP servers
- C. Logging every request
- D. Project notes Claude Code reads at the start of every session

<details><summary>Answer</summary>

**Answer: D** - It's project memory: how to test, style rules, what to avoid.

</details>
