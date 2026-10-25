---
type: quiz
title: "Quick check: why the envelope"
minutes: 11
---

### Q1. A script uses `out=$(claude -p "...")` and publishes `$out`. One night it publishes "Error: Reached max turns (1)". Why didn't anything stop it?

- A. Plain text output has no status; the script never looked at the exit code or an is_error field
- B. The model lied
- C. Cron hid the error
- D. max-turns doesn't work in -p

<details><summary>Answer</summary>

**Answer: A** - With --output-format json, is_error and subtype make failures machine-readable.

</details>

### Q2. Which envelope fields prove a run succeeded?

- A. result is non-empty
- B. session_id is set
- C. num_turns > 0
- D. is_error is false and subtype is success

<details><summary>Answer</summary>

**Answer: D** - A failed run can still have text in result.

</details>

### Q3. Your input file doesn't exist. What should the script do?

- A. Call claude anyway; it will say so
- B. Exit 2 before any model call
- C. Exit 0 with an empty output
- D. Retry three times

<details><summary>Answer</summary>

**Answer: B** - Bad input is the caller's problem, cheap to detect, and deserves its own code.

</details>

### Q4. Why keep `work/<name>.envelope.json` after publishing?

- A. It's required by Claude Code
- B. jq needs it
- C. For caching
- D. It holds the session_id and cost, which link the published artefact back to its transcript

<details><summary>Answer</summary>

**Answer: D** - When an output is questioned, the envelope is your audit trail.

</details>
