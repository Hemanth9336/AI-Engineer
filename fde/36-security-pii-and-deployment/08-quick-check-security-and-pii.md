---
type: quiz
title: "Quick check: security and PII"
minutes: 3
---

### Q1. What's the safest way to protect PII from a model provider?

- A. Don't send it: redact before the call
- B. Trust the contract
- C. Use HTTPS
- D. Ask the model to forget

<details><summary>Answer</summary>

**Answer: A** - Minimisation beats promises.

</details>

### Q2. Why apply the IBAN and card patterns before the phone pattern?

- A. Alphabetical order
- B. A broad phone pattern would match parts of IBANs or card numbers and leave the rest exposed
- C. Speed
- D. Regex requires it

<details><summary>Answer</summary>

**Answer: B** - Most specific first.

</details>

### Q3. The security team wants data kept in the EU and never used for training. Which deployment fits best?

- A. An enterprise API or VPC deployment in an EU region with zero-retention, no-training terms
- B. Any consumer chat app
- C. On-prem only
- D. A browser plugin

<details><summary>Answer</summary>

**Answer: A** - Match region and terms to the requirement.

</details>

### Q4. How do you prove redaction works?

- A. Say so in the slides
- B. Test once by hand
- C. Scan the actual outbound prompt log with a check that fails on any match
- D. Ask the model

<details><summary>Answer</summary>

**Answer: C** - Evidence from what was really sent.

</details>
