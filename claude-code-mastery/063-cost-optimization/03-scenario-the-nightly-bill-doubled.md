---
type: scenario
title: "Scenario: the nightly bill doubled"
minutes: 11
---

The nightly triage job cost about $4 a night for months. Since Monday it costs $9. Nobody changed the model. You have the envelopes for every run.

### Q1. What do you compare first?

- A. num_turns and usage.input_tokens per run, before and after Monday
- B. The model names
- C. duration_ms
- D. The prompt text

<details><summary>Answer</summary>

**Answer: A** - If the model and price are the same, cost moved because tokens moved; turns and input usually explain it.

</details>

### Q2. num_turns went from 3 to 7 per run. What's the likely cause?

- A. The model got worse
- B. Something made the agent loop more - a new tool, a failing command it retries, or a larger task
- C. Caching
- D. Timezones

<details><summary>Answer</summary>

**Answer: B** - Each extra turn re-sends the whole context; read one transcript to see why it loops.

</details>

### Q3. cache_read_input_tokens dropped to zero on Monday. What could do that?

- A. Nothing; caching is automatic
- B. A new API key
- C. The prompt prefix now changes every run - for example a timestamp or the run id added to the system prompt or CLAUDE.md
- D. Using haiku

<details><summary>Answer</summary>

**Answer: C** - Caching needs a byte-identical prefix; put variable data at the end.

</details>

### Q4. Which guard stops a single runaway night from costing $200?

- A. A cheaper model
- B. --max-budget-usd on the run, plus an alert on total_cost_usd
- C. Fewer cases
- D. Running weekly

<details><summary>Answer</summary>

**Answer: B** - A budget cap bounds the worst case; the alert tells you it happened.

</details>
