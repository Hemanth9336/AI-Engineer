---
type: quiz
title: "Quick check: hooks"
minutes: 5
---

### Q1. You want every file Claude edits to be formatted automatically. Which event?

- A. Notification
- B. UserPromptSubmit
- C. SessionStart
- D. PostToolUse with matcher Edit|Write

<details><summary>Answer</summary>

**Answer: D** - Run after the edit succeeds.

</details>

### Q2. A PreToolUse hook exits with code 2 and prints "deploys are blocked" to stderr. What happens?

- A. Nothing - only exit 1 blocks
- B. The tool runs anyway
- C. Claude Code crashes
- D. The tool call is blocked and Claude receives the message

<details><summary>Answer</summary>

**Answer: D** - Exit 2 blocks and feeds stderr to Claude.

</details>

### Q3. How does a hook find out which file was edited?

- A. It reads the transcript
- B. From $1
- C. From the JSON on stdin: tool_input.file_path
- D. From an environment variable named FILE

<details><summary>Answer</summary>

**Answer: C** - The event arrives as JSON on standard input.

</details>

### Q4. Why reference `$CLAUDE_PROJECT_DIR` in the hook command?

- A. It makes hooks faster
- B. It's required for every hook
- C. So the hook path works no matter which folder Claude is in
- D. It enables exit code 2

<details><summary>Answer</summary>

**Answer: C** - It's the project root.

</details>

### Q5. Why read a repository's hooks before trusting it?

- A. They slow Claude down
- B. They change the model
- C. Hooks run shell commands as you, with your files and credentials
- D. They're encrypted

<details><summary>Answer</summary>

**Answer: C** - A hook is code you're agreeing to run.

</details>
