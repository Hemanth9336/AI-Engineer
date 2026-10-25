---
type: scenario
title: "Scenario: a noisy log during an incident"
minutes: 11
---

It is 10:02. Checkout is failing for about a third of users. The shared log channel scrolls with gateway 502s, email worker retries, and a timeout warning from search. Your manager asks: "What broke, and what do we do right now?"

### Q1. Where do you start?

- A. The first error on the failing request path, following one request id
- B. The most frequent error message
- C. The newest line
- D. The search timeout

<details><summary>Answer</summary>

**Answer: A** - Frequency measures noise; the first error on the path measures cause.

</details>

### Q2. The first ERROR of the morning is an SMTP reset at 09:50, before any checkout failed. What is it?

- A. The root cause
- B. A red herring: earlier, and on an unrelated path
- C. Proof the network is down
- D. The trigger

<details><summary>Answer</summary>

**Answer: B** - Note it, but it can't explain checkouts failing from 09:58.

</details>

### Q3. The traceback ends with `KeyError: 'currency'` raised in `payments/client.py`, line 88, just after an orders deploy. What should you say right now?

- A. "Payments is broken, we will investigate"
- B. "Orders v2.3.0 stopped sending currency; roll it back now, then validate the field in payments"
- C. "Restart everything"
- D. "It is a network issue"

<details><summary>Answer</summary>

**Answer: B** - Name the trigger, the mitigation, and the durable fix.

</details>

### Q4. Why ask Claude for a structured triage rather than a summary paragraph?

- A. Each field (time, file:line, count) can be checked against the log and the code
- B. It is shorter
- C. Paragraphs are not allowed
- D. It is faster to render

<details><summary>Answer</summary>

**Answer: A** - During incidents, unverifiable claims cost the most.

</details>
