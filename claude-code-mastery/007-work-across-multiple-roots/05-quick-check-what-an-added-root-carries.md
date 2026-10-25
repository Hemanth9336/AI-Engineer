---
type: quiz
title: "Quick check: what an added root carries"
minutes: 8
---

### Q1. Which of these loads from a directory added with `--add-dir`?

- A. Its skills in .claude/skills/
- B. Its .claude/settings.json hooks
- C. Its permission rules
- D. Its CLAUDE.md, always

<details><summary>Answer</summary>

**Answer: A** - Flag-added roots contribute skills, commands, and subagents, but not hooks or permission rules.

</details>

### Q2. You list `../shared` under `permissions.additionalDirectories` in project settings. What does it grant?

- A. A second primary working directory
- B. File access plus skills and subagents
- C. Nothing until you run /cd
- D. File access only

<details><summary>Answer</summary>

**Answer: D** - Directories added through settings grant file access only; the configuration exceptions apply to flag-added roots.

</details>

### Q3. You want the agent to work from a different folder, with that folder's settings and CLAUDE.md. What do you run?

- A. /add-dir <path>
- B. /clear
- C. /cd <path>
- D. claude --resume

<details><summary>Answer</summary>

**Answer: C** - /cd moves the primary working directory and loads the new folder's configuration.

</details>

### Q4. A headless run without --add-dir tries to read ../secrets/key. What happens?

- A. It reads it - reads never prompt
- B. It is denied and listed in permission_denials
- C. It hangs waiting for approval
- D. Claude Code exits with an error

<details><summary>Answer</summary>

**Answer: B** - Reads outside the working directories need approval, which a -p run cannot give.

</details>
