---
type: quiz
title: "Quick check: when the loop stops"
minutes: 9
---

### Q1. A headless run read two files, ran one command, wrote one file, then answered. How many turns does the envelope report?

- A. 1
- B. 4
- C. 5
- D. It depends on the file sizes

<details><summary>Answer</summary>

**Answer: C** - Each model response is a turn: four tool-call turns plus the final answer make five.

</details>

### Q2. What normally ends the loop?

- A. Claude Code runs out of tools
- B. The first tool error
- C. A fixed timer of 60 seconds
- D. The model replies with text and no tool call

<details><summary>Answer</summary>

**Answer: D** - When the model answers without requesting a tool, the loop finishes with stop_reason end_turn.

</details>

### Q3. A run's envelope says `"subtype": "error_max_turns"`. What happened?

- A. The model refused the task
- B. A permission prompt timed out
- C. The JSON output was truncated
- D. It hit the --max-turns limit before finishing

<details><summary>Answer</summary>

**Answer: D** - error_max_turns means the loop was cut off by the turn limit you set.

</details>

### Q4. Where do you find the individual tool calls of a run you saved with --output-format json?

- A. In the envelope's result field
- B. In ~/.claude/projects/<folder>/<session_id>.jsonl
- C. In run.json under tools
- D. Nowhere - headless runs are not recorded

<details><summary>Answer</summary>

**Answer: B** - The envelope summarizes; the session transcript, keyed by session_id, records every step.

</details>
