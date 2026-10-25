---
type: scenario
title: "Scenario: the nightly job shipped a truncated answer"
minutes: 8
---

A nightly job runs `claude -p ... --output-format stream-json --verbose`, and a wrapper takes **the last assistant text** in the stream as the report it posts to the team channel. Last night's post read "All 214 migrations verified, safe to deploy." The run had actually been killed by the CI time limit halfway through.

### Q1. What was the wrapper's mistake?

- A. Using stream-json
- B. Posting at night
- C. Using --verbose
- D. Treating the last assistant text as the answer instead of requiring the final result event

<details><summary>Answer</summary>

**Answer: D** - Only the result event proves the run ended; text before it is work in progress.

</details>

### Q2. How should the wrapper have behaved when the stream ended without a result event?

- A. Post the last text with a warning
- B. Retry silently forever
- C. Fail closed: post nothing but 'run did not finish', exit non-zero
- D. Post the first text

<details><summary>Answer</summary>

**Answer: C** - Missing evidence means stop and say so.

</details>

### Q3. The job should also report migration counts reliably. What do you add?

- A. A longer prompt
- B. A bigger model
- C. --json-schema with a counts object, and a gate that checks structured_output exists and is consistent
- D. More turns

<details><summary>Answer</summary>

**Answer: C** - Constrained output gives the wrapper fields to check instead of prose to trust.

</details>

### Q4. Runs keep getting killed by the CI limit. What else do you change?

- A. Nothing
- B. Bound the run itself with --max-turns or --max-budget-usd so it ends with an error_* result before CI kills it
- C. Remove the CI limit
- D. Use text output

<details><summary>Answer</summary>

**Answer: B** - A run that ends itself reports why; a killed run reports nothing.

</details>
