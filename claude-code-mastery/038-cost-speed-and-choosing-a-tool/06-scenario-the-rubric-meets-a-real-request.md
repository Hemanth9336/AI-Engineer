---
type: scenario
title: "Scenario: the rubric meets a real request"
minutes: 6
---

Your rubric says: data questions with an oracle go to **haiku** (eligible: 3/3 passed, lowest cost per success); escalate to sonnet after two failed checks; re-measure when a model version changes. Requests start arriving.

### Q1. "How many EU refunds over 100.00 last month?" The data is in a CSV. Which tier?

- A. opus, to be safe
- B. sonnet, always
- C. haiku - it is the measured task class and it has an oracle
- D. Ask the team lead

<details><summary>Answer</summary>

**Answer: C** - Same task class, same oracle: apply the rubric.

</details>

### Q2. "Redesign the invoicing module's data model." Which part of the rubric applies?

- A. The haiku default
- B. Pick by median wall time
- C. Escalate to haiku
- D. None - it is a different task class; use your default for design work, or measure it

<details><summary>Answer</summary>

**Answer: D** - A rubric only covers the task classes you measured.

</details>

### Q3. Haiku fails the oracle check twice on a messy CSV. What does the rubric say?

- A. Retry haiku until it passes
- B. Ship the haiku answer
- C. Re-run on sonnet and log the escalation
- D. Lower the quality floor

<details><summary>Answer</summary>

**Answer: C** - Escalation is part of the rubric, and the log tells you when to revisit it.

</details>

### Q4. A new haiku version ships. What do you do with the rubric?

- A. Nothing, it is written
- B. Re-run measure.sh and update the numbers before relying on it
- C. Switch everything to the new model
- D. Delete it

<details><summary>Answer</summary>

**Answer: B** - New model versions are a re-measure trigger: the numbers belong to a model version.

</details>
