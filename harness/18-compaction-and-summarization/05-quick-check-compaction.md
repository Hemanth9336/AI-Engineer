---
type: quiz
title: "Quick check: compaction"
minutes: 4
---

### Q1. How is compaction different from dropping old turns?

- A. It's faster
- B. It deletes the system prompt
- C. It replaces old turns with a summary, so their important facts stay in context
- D. It needs a bigger model

<details><summary>Answer</summary>

**Answer: C** - Dropping loses everything in those turns; compaction keeps a short version of them.

</details>

### Q2. Which part of the history should compaction keep verbatim?

- A. The oldest tool results
- B. Only the assistant messages
- C. The system prompt, the task and the most recent turns
- D. Nothing - summarize everything

<details><summary>Answer</summary>

**Answer: C** - The model needs its rules, its goal and the result it just asked for.

</details>

### Q3. The summary says 'found the change ticket'. What's wrong?

- A. Nothing
- B. The exact ID is gone - the agent will need CHG-5521 character for character
- C. It's too long
- D. Summaries must be JSON

<details><summary>Answer</summary>

**Answer: B** - Ask the summarizer for exact names, numbers and IDs, and pin the ones that must never change.

</details>

### Q4. Your compaction test passes. How do you know it tests anything?

- A. It printed PASS
- B. Run it against a version without the fix - it must fail
- C. It ran quickly
- D. The model said so

<details><summary>Answer</summary>

**Answer: B** - A test that can't fail proves nothing.

</details>

### Q5. Why use a cheap model for summarizing?

- A. Cheap models are more accurate
- B. Expensive models can't summarize
- C. Compaction is an extra call on long runs; a small model does it well and keeps cost down
- D. The API requires it

<details><summary>Answer</summary>

**Answer: C** - Summarizing a few thousand tokens of tool output is an easy job.

</details>
