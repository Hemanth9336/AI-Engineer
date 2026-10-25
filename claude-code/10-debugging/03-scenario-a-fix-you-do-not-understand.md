---
type: scenario
title: "Scenario: a fix you do not understand"
minutes: 5
---

A test about invoice rounding has been failing for a week. You give Claude the failure and it comes back with a green test suite. The diff changes one line in `invoice.py` - `round(x, 2)` becomes `float(Decimal(str(x)).quantize(Decimal("0.01"), ROUND_HALF_UP))` - and edits the expected value in the test from `10.05` to `10.04`.

### Q1. What's the first problem with this change?

- A. It changed the test's expected value - the test no longer checks what it used to
- B. It's too short
- C. It uses the decimal module
- D. It was written by an AI

<details><summary>Answer</summary>

**Answer: A** - Editing the assertion to match the code can hide a real bug.

</details>

### Q2. You don't understand the Decimal line. What do you do?

- A. Revert it and fix it yourself without asking
- B. Merge it - the tests pass
- C. Ask Claude to explain the root cause and why this fixes it, with an example value
- D. Ask for a longer version

<details><summary>Answer</summary>

**Answer: C** - Never merge a fix you can't explain - ask for the reasoning.

</details>

### Q3. What request gives you a fix you can trust?

- A. "Try again"
- B. "Make the original test pass without changing the test, and add two more cases around .x5 rounding"
- C. "Make all tests green"
- D. "Remove the rounding test"

<details><summary>Answer</summary>

**Answer: B** - The test defines correct; more cases pin it down.

</details>
