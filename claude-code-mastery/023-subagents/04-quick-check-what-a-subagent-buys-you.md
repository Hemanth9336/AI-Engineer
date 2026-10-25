---
type: quiz
title: "Quick check: what a subagent buys you"
minutes: 9
---

### Q1. A subagent reads 40 files to answer your question. What lands in your main context window?

- A. Its final answer only
- B. All 40 files
- C. Nothing
- D. A summary of every tool call

<details><summary>Answer</summary>

**Answer: A** - Subagents work in their own window; only the result returns.

</details>

### Q2. Which subagent definition is safe for exploring an unfamiliar repo?

- A. tools omitted
- B. tools: Read, Grep, Glob
- C. tools: Bash, Write
- D. model: opus

<details><summary>Answer</summary>

**Answer: B** - Read-only tools mean the scout cannot change anything.

</details>

### Q3. Why might the main agent read all the files itself instead of delegating?

- A. Subagents are disabled in -p
- B. --agents only works interactively
- C. Subagents need opus
- D. The prompt did not ask for delegation and the agent's description did not match

<details><summary>Answer</summary>

**Answer: D** - Ask for the fan-out explicitly and write a description that matches the job.

</details>

### Q4. Where do you find proof that three scouts ran?

- A. In CLAUDE.md
- B. In git log
- C. In the envelope's result
- D. In ~/.claude/projects/<project>/<session>/subagents/

<details><summary>Answer</summary>

**Answer: D** - Each subagent leaves a transcript and a meta file next to the main session.

</details>
