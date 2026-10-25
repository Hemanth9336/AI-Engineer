---
type: quiz
title: "Quick check: packaging skills"
minutes: 5
---

### Q1. What does the model see about a skill before it calls it?

- A. The whole SKILL.md
- B. The extra files
- C. Nothing
- D. Only its name and description

<details><summary>Answer</summary>

**Answer: D** - Which is why the description decides whether the skill is used.

</details>

### Q2. Why not put every workflow's instructions in CLAUDE.md?

- A. CLAUDE.md can't hold steps
- B. It's loaded on every run - rarely used workflows waste the window
- C. Skills are faster to write
- D. Models ignore CLAUDE.md

<details><summary>Answer</summary>

**Answer: B** - Load instructions when they're needed.

</details>

### Q3. Which description will be picked most reliably for 'write the changelog for v2.4'?

- A. "Draft release notes for a ledger-api version from its change list. Use when asked for release notes, a changelog, or what's new."
- B. "Helper for docs"
- C. "release-notes"
- D. "Important skill"

<details><summary>Answer</summary>

**Answer: A** - What + when, with the words users use.

</details>

### Q4. The change list for the requested version doesn't exist. What should a good skill tell the model?

- A. Say the file is missing and stop
- B. Make up likely changes
- C. Use the previous version's list
- D. Retry forever

<details><summary>Answer</summary>

**Answer: A** - Explicit failure handling prevents invention.

</details>

### Q5. You need a rule that must hold on every run, whatever the model decides. Skill or hook?

- A. Skill
- B. Neither
- C. Either
- D. Hook (or a permission rule)

<details><summary>Answer</summary>

**Answer: D** - Skills are instructions; hooks are enforcement.

</details>
