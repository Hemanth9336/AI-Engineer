---
type: quiz
title: "Quick check: latency and streaming"
minutes: 4
---

### Q1. What does streaming improve?

- A. Time to first visible text - perceived latency
- B. Total generation time
- C. Answer quality
- D. Token cost

<details><summary>Answer</summary>

**Answer: A** - Same finish time, much earlier start.

</details>

### Q2. What's usually the biggest real latency win?

- A. A faster laptop
- B. Higher temperature
- C. More retrieved chunks
- D. Fewer output tokens - shorter answers

<details><summary>Answer</summary>

**Answer: D** - Generation time scales with output length.

</details>

### Q3. Why set max_retries=0 on a primary client that has a fallback?

- A. Retries cost more
- B. The SDK requires it
- C. Retrying a slow primary multiplies the wait before the fallback runs
- D. To avoid logging

<details><summary>Answer</summary>

**Answer: C** - Let the fallback handle the failure.

</details>

### Q4. The primary returns HTTP 400 (bad request). Should you fall back?

- A. No - the request itself is wrong; fix it, the fallback will fail too
- B. Yes, always
- C. Only at night
- D. Only for lab-smart

<details><summary>Answer</summary>

**Answer: A** - Fall back on availability errors, not on your own bugs.

</details>
