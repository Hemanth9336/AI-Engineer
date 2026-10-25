---
type: scenario
title: "Scenario: the generated suite passes on the first run"
minutes: 11
---

A teammate asks Claude for tests on a legacy billing module. Thirty tests appear, all green on the first run, and coverage reports 94%. The teammate wants to merge.

### Q1. What does "all green on the first run" prove about the suite?

- A. That the module is correct
- B. That coverage is high enough
- C. Only that the tests agree with the current code, bugs included
- D. That the tests are deterministic

<details><summary>Answer</summary>

**Answer: C** - Tests generated from running code can encode its bugs. They need to be able to fail.

</details>

### Q2. What is the quickest way to measure whether these tests can catch bugs?

- A. Raise coverage to 100%
- B. Ask Claude if the tests are good
- C. Run the suite twice
- D. Run a few mutants of the riskiest lines and see which survive

<details><summary>Answer</summary>

**Answer: D** - Coverage says the lines ran; mutants say the assertions would notice a change.

</details>

### Q3. A test reads `self.assertEqual(total(items), total(items))`. Coverage counts it. What's wrong?

- A. Nothing
- B. It is too slow
- C. It should use assertTrue
- D. The expected value comes from the code under test, so it can never fail

<details><summary>Answer</summary>

**Answer: D** - Expected values must come from the spec, not from the implementation.

</details>

### Q4. Two mutants survive. What do you ask Claude for?

- A. Tests that kill those specific mutants, with hand-computed expectations
- B. Delete the mutants
- C. More tests in general
- D. Lower the bar

<details><summary>Answer</summary>

**Answer: A** - Survivors are precise feedback: each one names a behavior no test pins down.

</details>
