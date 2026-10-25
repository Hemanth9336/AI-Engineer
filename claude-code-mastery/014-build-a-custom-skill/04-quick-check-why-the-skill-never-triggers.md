---
type: quiz
title: "Quick check: why the skill never triggers"
minutes: 9
---

### Q1. Your SKILL.md starts with a title line, then the `---` frontmatter. What happens?

- A. The frontmatter is ignored and treated as content, so the description never registers
- B. It works normally
- C. Claude Code refuses to start
- D. The skill runs twice

<details><summary>Answer</summary>

**Answer: A** - Frontmatter is only read when the opening --- is the first line of the file.

</details>

### Q2. Claude never picks your skill on its own, but `/release` works. Most likely cause?

- A. The folder name is wrong
- B. The skill is too short
- C. allowed-tools is missing
- D. disable-model-invocation: true, or a description that does not match what people ask

<details><summary>Answer</summary>

**Answer: D** - Automatic use depends on the description, and disable-model-invocation turns it off.

</details>

### Q3. `/standup` aborts with "Shell command permission check failed". Fix?

- A. Use --dangerously-skip-permissions
- B. Rename SKILL.md to skill.md
- C. Move the skill to ~/.claude
- D. Pre-approve the injected command with allowed-tools in the frontmatter

<details><summary>Answer</summary>

**Answer: D** - Injected commands that a rule would not allow abort the skill; allowed-tools grants them for the skill.

</details>

### Q4. You wrote `allowed_tools: Bash(git log *)` and it has no effect. Why?

- A. Field names must match exactly - it is allowed-tools; unknown fields are silently ignored
- B. Bash cannot be pre-approved
- C. It needs quotes
- D. allowed-tools only works in plugins

<details><summary>Answer</summary>

**Answer: A** - Claude Code ignores unrecognized frontmatter fields without an error.

</details>
