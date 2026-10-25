---
type: quiz
title: "Quick check: headless Claude Code"
minutes: 4
---

### Q1. What does `claude -p "prompt"` print to standard output by default?

- A. Only the final answer text
- B. The full conversation
- C. A JSON object
- D. Nothing - it writes to a file

<details><summary>Answer</summary>

**Answer: A** - Text format is just the answer.

</details>

### Q2. A script needs the answer and whether the run failed. Which flag?

- A. `--verbose`
- B. `--output-format json`, then read `.result` and `.is_error`
- C. `--max-turns 1`
- D. `--model haiku`

<details><summary>Answer</summary>

**Answer: B** - The JSON result carries both.

</details>

### Q3. What does `cat error.log | claude -p "explain"` do?

- A. Writes the explanation into error.log
- B. Ignores the pipe
- C. Fails - -p can't read stdin
- D. Sends the log content to Claude along with the prompt

<details><summary>Answer</summary>

**Answer: D** - Stdin is added to the prompt.

</details>

### Q4. A headless run tries `rm -rf build/` and you didn't allow it. What happens?

- A. The run crashes immediately
- B. It runs
- C. Claude waits for you to type y
- D. It's denied and listed in `permission_denials`; the run continues without it

<details><summary>Answer</summary>

**Answer: D** - Headless runs can't ask, so they deny.

</details>

### Q5. Which flag must go with `--output-format stream-json`?

- A. `--stream`
- B. `--json`
- C. `--verbose`
- D. `--debug`

<details><summary>Answer</summary>

**Answer: C** - stream-json in print mode requires --verbose.

</details>
