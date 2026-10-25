---
type: quiz
title: "Quick check: command scope"
minutes: 9
---

### Q1. You want /pr-summary in every repo you work on, but not forced on teammates. Where does the file go?

- A. Each repo's .claude/commands/
- B. ~/.claude/commands/pr-summary.md
- C. CLAUDE.md
- D. ~/.claude/skills/pr-summary.md

<details><summary>Answer</summary>

**Answer: B** - User-level commands load in all your projects and are not committed anywhere.

</details>

### Q2. A project has both .claude/skills/deploy/SKILL.md and .claude/commands/deploy.md. What does /deploy run?

- A. The command file
- B. Both, in order
- C. The skill
- D. Neither - it errors

<details><summary>Answer</summary>

**Answer: C** - When a skill and a command share a name, the skill wins.

</details>

### Q3. Your command says `Summarize ticket $1`. You run `/ticket 4521`. What does Claude see?

- A. Summarize ticket $1, plus ARGUMENTS: 4521 appended
- B. Summarize ticket 4521
- C. An error
- D. Summarize ticket

<details><summary>Answer</summary>

**Answer: A** - Positional arguments are 0-based; with one argument $1 is empty-handed, so it stays literal and the args are appended.

</details>

### Q4. How does a CI job run the project command /release-notes for version 3.0.0?

- A. claude --command release-notes 3.0.0
- B. It cannot - commands are interactive only
- C. cat .claude/commands/release-notes.md | sh
- D. claude -p "/release-notes 3.0.0"

<details><summary>Answer</summary>

**Answer: D** - -p accepts a slash command as the prompt.

</details>
