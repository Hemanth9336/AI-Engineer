---
type: quiz
title: "Quick check: what CI actually reads"
minutes: 11
---

### Q1. A step runs `claude -p "..." --output-format json | jq -r .result`. Claude hits `--max-turns`. Without pipefail, what does CI see?

- A. Exit 0 - jq succeeded, so the failure is hidden
- B. Exit 1
- C. Exit 2
- D. A timeout

<details><summary>Answer</summary>

**Answer: A** - A pipeline returns the last command's status unless pipefail is set.

</details>

### Q2. The review run exits 0 but the envelope has no `structured_output`. What should the gate do?

- A. Fail closed with a distinct 'review broken' exit code
- B. Parse the prose result for the word 'block'
- C. Pass, since the exit code was 0
- D. Retry forever

<details><summary>Answer</summary>

**Answer: A** - Without a valid structured answer there is no verdict, and no verdict must never mean pass.

</details>

### Q3. Why give 'tests failed', 'review blocked', and 'review step broken' different exit codes?

- A. CI requires it
- B. No reason
- C. To save tokens
- D. So a red build says what to do next: fix code, address findings, or fix the pipeline

<details><summary>Answer</summary>

**Answer: D** - Distinct signals also let you alert on infrastructure failures separately.

</details>

### Q4. Which file must never contain the API key?

- A. The CI secret store
- B. ci.sh or any file in the repo
- C. The runner's environment
- D. None

<details><summary>Answer</summary>

**Answer: B** - The key comes from the secret store into ANTHROPIC_API_KEY at run time.

</details>

### Q5. Why run the paid review only after the tests pass?

- A. Claude can't read failing code
- B. Failing tests already fail the build; reviewing broken code wastes money and time
- C. Tests need the API key
- D. It's required by the action

<details><summary>Answer</summary>

**Answer: B** - Order cheap, deterministic gates before expensive, probabilistic ones.

</details>
