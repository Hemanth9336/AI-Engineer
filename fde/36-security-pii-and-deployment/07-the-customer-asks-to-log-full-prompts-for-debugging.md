---
type: scenario
title: "The customer asks to log full prompts for debugging"
minutes: 3
---

Two weeks into the Kestrel Foods pilot, their IT lead says: "Debugging is painful. Can you just log the full original prompts and answers - unredacted - to our shared logging cluster? Everyone in IT can read it, and it keeps data for two years."

### Q1. What's the main risk?

- A. Disk space
- B. Slower logging
- C. Customer PII - emails, phones, IBANs, card numbers - copied to a widely readable store for two years, which the redaction was meant to prevent
- D. The model will see the logs

<details><summary>Answer</summary>

**Answer: C** - Logs are the most common PII leak.

</details>

### Q2. What can you offer that still makes debugging easy?

- A. Nothing
- B. Log redacted prompts and full metadata (request id, retrieval ids, model, prompt version) by default; keep originals only in a restricted store with short retention, accessed by request id
- C. Email prompts to IT
- D. Log everything but compress it

<details><summary>Answer</summary>

**Answer: B** - Debuggability without spreading raw PII.

</details>

### Q3. Who should approve any change to what's logged?

- A. You alone
- B. Whoever asks first
- C. The model provider
- D. The customer's privacy/security owner (for example the DPO), in writing

<details><summary>Answer</summary>

**Answer: D** - Data handling changes need the data owner's sign-off.

</details>
