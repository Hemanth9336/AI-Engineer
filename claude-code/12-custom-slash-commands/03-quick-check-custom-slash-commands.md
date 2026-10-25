---
type: quiz
title: "Quick check: custom slash commands"
minutes: 4
---

### Q1. Where do you put a command the whole team should get with the repo?

- A. `/tmp/commands`
- B. `~/.claude/commands/`
- C. CLAUDE.md
- D. `.claude/commands/` in the project, committed

<details><summary>Answer</summary>

**Answer: D** - Project commands travel with the repository.

</details>

### Q2. You run `/deploy-notes staging 42`. What is `$ARGUMENTS`?

- A. Empty
- B. `deploy-notes`
- C. `staging`
- D. `staging 42`

<details><summary>Answer</summary>

**Answer: D** - Everything after the command name.

</details>

### Q3. What does the `description` front matter do?

- A. It's shown in the / menu so people know what the command does
- B. It's sent as the system prompt
- C. It names the file
- D. It sets the model

<details><summary>Answer</summary>

**Answer: A** - It's the command's help text.

</details>

### Q4. A command body contains !`git diff`. When does that run?

- A. After Claude answers
- B. Never - it's a comment
- C. Before the prompt is sent - its output is included in the prompt (if allowed by allowed-tools)
- D. Only in plan mode

<details><summary>Answer</summary>

**Answer: C** - It injects live context into the prompt.

</details>

### Q5. How do you use a custom command from a script?

- A. `claude --command changelog`
- B. `claude -p "/changelog v1.4"`
- C. You can't - commands are console-only
- D. `bash .claude/commands/changelog.md`

<details><summary>Answer</summary>

**Answer: B** - Slash commands work in print mode.

</details>
