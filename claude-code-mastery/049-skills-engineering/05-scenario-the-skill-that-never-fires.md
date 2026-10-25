---
type: scenario
title: "Scenario: the skill that never fires"
minutes: 7
---

A teammate's `deploy-notes` skill "works when I type `/deploy-notes`" but Claude never uses it on its own. You open `SKILL.md` and the listing.

### Q1. The frontmatter begins on line 3, after a `# Deploy notes` title and a blank line. What happens?

- A. Claude Code moves the title below the frontmatter
- B. The `---` block is treated as plain content, so the skill has no description
- C. Only the name is lost
- D. Nothing; frontmatter can start anywhere

<details><summary>Answer</summary>

**Answer: B** - Frontmatter is read only when the opening `---` is the first line of the file.

</details>

### Q2. The description is 1,900 characters, and the trigger phrase "release notes" appears at character 1,700. Why doesn't it fire?

- A. Descriptions over 1,000 characters are ignored
- B. The listing cuts description plus when_to_use at 1,536 characters, so the phrase is never seen
- C. Long descriptions switch the skill to manual mode
- D. The model reads only the first sentence

<details><summary>Answer</summary>

**Answer: B** - Put the key use case first; anything after the cap doesn't reach the model.

</details>

### Q3. `claude plugin validate .` reports `YAML frontmatter failed to parse` for this skill. What does that mean at runtime?

- A. The skill doesn't load at all
- B. Only allowed-tools is dropped
- C. It loads with empty metadata: /deploy-notes works, but there is no description to match
- D. Claude Code repairs the YAML

<details><summary>Answer</summary>

**Answer: C** - That explains exactly the reported symptom: manual invocation works, automatic selection doesn't.

</details>

### Q4. The frontmatter has `disable-model-invocation: true`. Is that a bug?

- A. Yes, always remove it
- B. It only affects subagents
- C. Only if the skill should fire automatically; it deliberately limits the skill to /deploy-notes
- D. It hides the skill from the / menu

<details><summary>Answer</summary>

**Answer: C** - It's the right choice for side-effecting workflows, and the wrong one for a skill you want Claude to pick.

</details>

### Q5. After fixing the description, how do you show the fix works, and keep it working?

- A. Ask once in a session and watch
- B. Run should-fire and should-not prompts headless (or in claude plugin eval) and assert the Skill call
- C. Re-run claude plugin validate
- D. Count the description's keywords

<details><summary>Answer</summary>

**Answer: B** - Validation proves the file loads; only runs prove selection. Keep the case matrix and re-run it after every edit.

</details>
