---
type: scenario
title: "Scenario: the specialist never gets picked"
minutes: 9
---

Your team added `.claude/agents/db-migrations.md` six weeks ago: a careful reviewer for SQL migrations. Nobody has seen it run. Its frontmatter reads `name: db-migrations` and `description: Database helper.` Meanwhile engineers keep asking Claude to "check this migration before I merge".

### Q1. What is the most likely reason it never runs?

- A. Agents only run in plan mode
- B. It needs model: opus
- C. The description is too vague to match "check this migration"
- D. Project agents are disabled by default

<details><summary>Answer</summary>

**Answer: C** - Delegation is driven by the description; "Database helper" says nothing about reviewing migrations.

</details>

### Q2. Which description fixes it?

- A. Reviews SQL migration files for locking, data loss, and missing rollbacks. Use proactively before merging any change under migrations/.
- B. Helps with databases
- C. The best agent
- D. Use for everything

<details><summary>Answer</summary>

**Answer: A** - Concrete triggers in the users' own words make automatic delegation work.

</details>

### Q3. In CI you need the review to run every time, not just when Claude decides. How?

- A. Hope the description matches
- B. Run it twice
- C. Add it to CLAUDE.md
- D. Name it in the prompt, or run claude -p --agent db-migrations

<details><summary>Answer</summary>

**Answer: D** - Naming the agent or making it the main agent removes the guesswork.

</details>
