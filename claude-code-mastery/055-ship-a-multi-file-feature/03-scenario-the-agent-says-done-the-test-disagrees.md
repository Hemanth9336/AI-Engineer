---
type: scenario
title: "Scenario: the agent says done, the test disagrees"
minutes: 11
---

An execute run ends with "Implemented the feature; all tests pass." Your `verify.sh` fails at `old tasks.json without done`.

### Q1. Both can be true at once. How?

- A. They can't; the agent lied
- B. verify.sh is flaky
- C. The agent's tests pass, but none of them loads an old-format file - the gap is in the tests, not in the claim
- D. The cache is stale

<details><summary>Answer</summary>

**Answer: C** - 'All tests pass' is a statement about the tests that exist.

</details>

### Q2. What's the best next prompt?

- A. "Fix it."
- B. Start over in a new session
- C. "Try harder."
- D. "verify.sh fails: loading [{\"id\": 1, \"title\": \"Legacy\"}] raises KeyError 'done'. Add a test for old files, make it pass, run ./verify.sh."

<details><summary>Answer</summary>

**Answer: D** - Give the failing evidence, ask for a regression test, and let the agent run your verifier.

</details>

### Q3. Should you let the agent edit `verify.sh` to make it pass?

- A. Yes
- B. No - keep the verifier yours; deny Edit(verify.sh) or keep it outside the agent's write scope
- C. Only in plan mode
- D. Only with a commit

<details><summary>Answer</summary>

**Answer: B** - A verifier the agent can change stops being independent.

</details>

### Q4. Which plan item would have prevented this?

- A. A compatibility section: old files have no done key and must load as not done
- B. A longer plan
- C. Fewer files
- D. Using sonnet

<details><summary>Answer</summary>

**Answer: A** - Data compatibility belongs in the plan you review before any edit.

</details>
