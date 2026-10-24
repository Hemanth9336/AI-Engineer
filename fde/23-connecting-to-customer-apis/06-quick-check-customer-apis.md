---
type: quiz
title: "Quick check: customer APIs"
minutes: 4
---

### Q1. The orders API returns 404 for an order id. What should the tool return?

- A. Raise an exception
- B. {"error": "order not found"} - it's an answer, not a crash
- C. An empty dict
- D. Retry three times

<details><summary>Answer</summary>

**Answer: B** - 404 is information the model can use.

</details>

### Q2. Why must every API call have a timeout?

- A. Without one, a hung API hangs the assistant
- B. To save money
- C. APIs require it
- D. For logging

<details><summary>Answer</summary>

**Answer: A** - Bounded waits keep the assistant responsive.

</details>

### Q3. Where should the API token be added to the request?

- A. In the system prompt
- B. In the tool description
- C. In your code, as a header - the model never sees it
- D. In the user message

<details><summary>Answer</summary>

**Answer: C** - Credentials stay out of the model's context.

</details>

### Q4. Which credential should a support bot use for an orders API?

- A. An engineer's personal admin key
- B. The CEO's account
- C. A service account with read-only access to orders
- D. No credentials

<details><summary>Answer</summary>

**Answer: C** - Narrow scope limits the blast radius.

</details>
