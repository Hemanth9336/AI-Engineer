---
type: scenario
title: "Scenario: workers flood the coordinator"
minutes: 11
---

Your coordinator fans 40 files out to a `summarizer` worker. Each worker returns a 2,000-word summary. By file 25 the coordinator forgets the output format, and the run costs five times your estimate.

### Q1. What is the root cause?

- A. The model is too small
- B. The schema was wrong
- C. Workers ran in parallel
- D. Every worker reply lands in the coordinator's context; 40 essays crowd out its instructions and inflate every later turn

<details><summary>Answer</summary>

**Answer: D** - The coordinator pays for, and has to reason over, everything it receives.

</details>

### Q2. Which change helps most?

- A. Make workers reply in a tight fixed format (JSON or one line per item) and say 'only'
- B. Use opus for the coordinator
- C. Run fewer workers at a time
- D. Increase max turns

<details><summary>Answer</summary>

**Answer: A** - Small structured replies keep the coordinator focused and cheap.

</details>

### Q3. Workers also need the full text of each file. Where should it go?

- A. Paste it into the Agent prompt
- B. The coordinator reads all 40 first
- C. Into CLAUDE.md
- D. Let the worker read the file itself (Read tool) so the contents stay in the worker's context

<details><summary>Answer</summary>

**Answer: D** - Pass paths, not contents, when the worker can read them; contents then never touch the coordinator.

</details>

### Q4. Where should the final document's formatting happen?

- A. In the coordinator's last message
- B. In code: --json-schema for the data, a renderer for Markdown
- C. In each worker
- D. In a second coordinator

<details><summary>Answer</summary>

**Answer: B** - Deterministic rendering means formatting bugs are fixed once, in code.

</details>
