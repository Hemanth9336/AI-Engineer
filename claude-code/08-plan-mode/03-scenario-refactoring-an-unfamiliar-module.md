---
type: scenario
title: "Scenario: refactoring an unfamiliar module"
minutes: 4
---

You've been asked to add retry logic to `payments/gateway.py`, a 900-line module written by someone who left last year. It has few tests, and `charge()` is called from the web app, a nightly batch job, and an admin script.

### Q1. How do you start?

- A. Read all 900 lines yourself before involving Claude
- B. acceptEdits: "add retries to charge()" and review the diff later
- C. Plan mode: ask Claude to map who calls `charge()`, what it does on failure, and propose a plan - no edits
- D. bypassPermissions so it can test against the real gateway

<details><summary>Answer</summary>

**Answer: C** - Unknown, risky, widely-used code is exactly what plan mode is for.

</details>

### Q2. The plan says: "wrap charge() in a retry loop, 3 attempts". What's missing before you approve?

- A. A bigger number of retries
- B. Nothing - it's clear
- C. Whether a retry could charge a customer twice, and how the change will be tested
- D. Which model wrote it

<details><summary>Answer</summary>

**Answer: C** - Payments retries need idempotency thinking and a test plan.

</details>

### Q3. What's a sensible first implementation step?

- A. Add tests that pin today's behavior of `charge()`, then make the change
- B. Rewrite the whole module in one go
- C. Delete the admin script that calls it
- D. Deploy and watch the logs

<details><summary>Answer</summary>

**Answer: A** - Characterization tests first make every later step verifiable.

</details>
