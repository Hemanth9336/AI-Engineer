---
type: scenario
title: "Scenario: where does the rule belong"
minutes: 9
---

You are setting up instructions for a 40-person engineering org. Over one week you collect requests: your own preference for terse answers, the payments repo's "money is integer cents" rule, the security team's "never paste customer data into prompts", and your personal staging URL for the payments repo.

### Q1. Where does "money is integer cents" belong?

- A. ~/.claude/CLAUDE.md
- B. The payments repo's CLAUDE.md
- C. Managed policy
- D. CLAUDE.local.md

<details><summary>Answer</summary>

**Answer: B** - It is a rule about that codebase, shared with everyone who works on it.

</details>

### Q2. Where does your personal staging URL for the payments repo go?

- A. The payments CLAUDE.md
- B. Managed policy
- C. CLAUDE.local.md in the payments repo, gitignored
- D. A commit message

<details><summary>Answer</summary>

**Answer: C** - Personal, project-specific details go in the local file that is never committed.

</details>

### Q3. The security rule must reach every developer and every repo. Where?

- A. Each repo's CLAUDE.md
- B. Everyone's ~/.claude/CLAUDE.md
- C. The managed policy CLAUDE.md, backed by enforced managed settings or hooks
- D. The company wiki

<details><summary>Answer</summary>

**Answer: C** - Managed files apply machine-wide and cannot be skipped by users; enforcement needs settings or hooks.

</details>

### Q4. Your terse-answers preference conflicts with a repo rule asking for detailed summaries. What happens?

- A. Both load; without an explicit override the model may follow either
- B. The user rule always wins
- C. The project rule always wins
- D. Claude Code refuses to start

<details><summary>Answer</summary>

**Answer: A** - Instruction files are concatenated; resolve conflicts by making one rule explicitly take precedence.

</details>
