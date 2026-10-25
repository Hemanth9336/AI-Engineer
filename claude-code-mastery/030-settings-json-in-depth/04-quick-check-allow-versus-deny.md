---
type: quiz
title: "Quick check: allow versus deny"
minutes: 9
---

### Q1. Your user settings allow `Bash(rm *)`. The project denies `Bash(rm -rf *)`. Claude runs `rm -rf build`. What happens?

- A. Denied - lists merge and deny is checked first
- B. Allowed - user settings are yours
- C. Claude is asked
- D. It depends on the model

<details><summary>Answer</summary>

**Answer: A** - Rules from all layers combine; any matching deny wins.

</details>

### Q2. A rule is in `ask`. You run `claude -p` in CI. What happens when Claude needs it?

- A. CI waits for input
- B. It is allowed
- C. The call is refused
- D. The run crashes

<details><summary>Answer</summary>

**Answer: C** - Headless runs cannot answer prompts, so ask behaves as a refusal.

</details>

### Q3. You put `"model": "opus"` in settings.local.json; the project file says `"model": "sonnet"`. Which applies to you?

- A. sonnet
- B. Neither
- C. Whichever was written last
- D. opus

<details><summary>Answer</summary>

**Answer: D** - Project local sits above project; plain keys take the highest layer's value.

</details>

### Q4. You added allow rules to `.claude/settings.json` in a freshly cloned repo, but Claude still asks. Why?

- A. The folder has not been trusted yet
- B. Allow rules need a restart
- C. Allow rules only work in user settings
- D. JSON comments

<details><summary>Answer</summary>

**Answer: A** - Project allow rules take effect once you accept the trust prompt for the folder.

</details>
