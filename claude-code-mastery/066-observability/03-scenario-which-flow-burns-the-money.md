---
type: scenario
title: "Scenario: which flow burns the money"
minutes: 11
---

Finance asks why agent spend went from $300 to $1,100 this month. Five flows run through your `run.sh`, and `metrics/runs.jsonl` has 9,400 rows.

### Q1. What's your first query?

- A. Read the last 50 rows
- B. Group by flow and sum cost_usd, sorted descending - then compare with last month's rows
- C. Count rows per day
- D. Average duration

<details><summary>Answer</summary>

**Answer: B** - Find the flow before finding the cause.

</details>

### Q2. `pr-review` went from 400 runs to 3,100. Cost per run is flat. What next?

- A. Switch it to haiku
- B. Find what triggers it - a CI change that runs it on every push instead of on pull requests is the usual cause
- C. Raise the budget
- D. Delete the flow

<details><summary>Answer</summary>

**Answer: B** - Volume, not price, moved; fix the trigger.

</details>

### Q3. `triage` runs are the same count, but cost per run tripled. Where do you look?

- A. The finance dashboard
- B. Cron logs
- C. The model's release notes
- D. num_turns and input_tokens per row, then one expensive run's transcript via its session_id

<details><summary>Answer</summary>

**Answer: D** - Rows show where; the transcript shows why.

</details>

### Q4. 1,200 rows have `subtype: unparsable`. Is that a cost problem?

- A. No, they cost nothing
- B. It's a blind spot - those runs may have spent money the envelope never reported; fix whatever breaks their output
- C. It's normal
- D. Delete those rows

<details><summary>Answer</summary>

**Answer: B** - Unmeasured runs are where surprises hide.

</details>
