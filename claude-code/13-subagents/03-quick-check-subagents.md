---
type: quiz
title: "Quick check: subagents"
minutes: 4
---

### Q1. What's the main benefit of running the test suite in a subagent?

- A. The long test output stays in the subagent's context; the main session gets a short report
- B. Tests run faster
- C. The subagent can fix the tests
- D. It avoids using any model

<details><summary>Answer</summary>

**Answer: A** - Isolation keeps the main context clean.

</details>

### Q2. Which field does Claude read to decide when to delegate to a subagent automatically?

- A. name
- B. description
- C. model
- D. tools

<details><summary>Answer</summary>

**Answer: B** - Write descriptions that say when to use it.

</details>

### Q3. A code-review subagent should never change files. How do you enforce that?

- A. Set model: haiku
- B. Say "please don't edit" in the main prompt
- C. `tools: Read, Bash` (no Write/Edit) in its front matter
- D. Put it in ~/.claude/agents

<details><summary>Answer</summary>

**Answer: C** - Tool restrictions are enforced; requests are not.

</details>

### Q4. What does a subagent know about your main conversation?

- A. The last three messages
- B. Everything said so far
- C. Only what's in the task it was given and its own instructions
- D. Your CLAUDE.md only

<details><summary>Answer</summary>

**Answer: C** - It starts fresh - give it what it needs.

</details>

### Q5. Where do you put a subagent the whole team should share?

- A. `~/.claude/agents/`
- B. `.claude/agents/` in the repo
- C. CLAUDE.md
- D. `.mcp.json`

<details><summary>Answer</summary>

**Answer: B** - Project agents travel with the repository.

</details>
