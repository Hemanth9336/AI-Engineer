---
type: quiz
title: "Quick check: when a PostToolUse hook runs"
minutes: 9
---

### Q1. Claude's Write call fails because the folder does not exist. Does your PostToolUse hook run?

- A. Yes, PostToolUse runs after every call
- B. Only with matcher *
- C. No - failed calls go to PostToolUseFailure
- D. Only in -p mode

<details><summary>Answer</summary>

**Answer: C** - PostToolUse is for successful calls; register the same script under PostToolUseFailure to see failures.

</details>

### Q2. Claude runs `sed -i 's/a/b/' notes/x.md` with Bash. Your hook's matcher is `Write|Edit`. What gets audited?

- A. The sed edit, as an Edit
- B. The hook errors
- C. Both
- D. Nothing - the tool was Bash

<details><summary>Answer</summary>

**Answer: D** - Matchers filter on the tool name. Watch the disk (FileChanged or git status) if any rewrite must be caught.

</details>

### Q3. Your hook prints `logging...` and then the JSON object. What happens?

- A. Claude sees both
- B. Claude Code strips the first line
- C. The output is not one JSON object, so it is treated as plain text and the additionalContext is lost
- D. The tool call is blocked

<details><summary>Answer</summary>

**Answer: C** - Stdout must be exactly one JSON object for its fields to apply.

</details>

### Q4. Which matcher matches Edit but **not** NotebookEdit?

- A. Edit.*
- B. .*Edit
- C. Edit
- D. Edit|Notebook

<details><summary>Answer</summary>

**Answer: C** - A plain name is an exact match; anything with regex characters is an unanchored regex.

</details>
