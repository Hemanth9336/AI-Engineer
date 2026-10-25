---
type: quiz
title: "Quick check: matching models to jobs"
minutes: 9
---

### Q1. A nightly script classifies 5,000 short log lines into five categories. Which model do you try first?

- A. opus
- B. opusplan
- C. haiku
- D. sonnet[1m]

<details><summary>Answer</summary>

**Answer: C** - High-volume, simple classification is the job the fastest, cheapest model is for - measure before moving up.

</details>

### Q2. You need a plan for a risky refactor, then a lot of routine edits. Which alias fits?

- A. haiku
- B. sonnet
- C. default
- D. opusplan

<details><summary>Answer</summary>

**Answer: D** - opusplan uses Opus while planning and Sonnet while executing.

</details>

### Q3. Both ANTHROPIC_MODEL=opus and `--model haiku` are set for a run. Which model answers?

- A. haiku
- B. opus
- C. sonnet
- D. the settings default

<details><summary>Answer</summary>

**Answer: A** - --model beats the environment variable, which beats the settings key.

</details>

### Q4. How do you confirm which model actually answered a headless run?

- A. The result text
- B. modelUsage keys in the JSON envelope
- C. duration_ms
- D. The session file name

<details><summary>Answer</summary>

**Answer: B** - modelUsage is keyed by the model that served the run.

</details>
