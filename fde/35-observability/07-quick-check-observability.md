---
type: quiz
title: "Quick check: observability"
minutes: 3
---

### Q1. Why must failed calls be logged too?

- A. They cost money
- B. The SDK requires it
- C. Otherwise the log hides the incidents you'll be asked about
- D. To fill disk

<details><summary>Answer</summary>

**Answer: C** - Failures are what you investigate.

</details>

### Q2. What does a request id give you?

- A. Security
- B. Cheaper tokens
- C. Lower latency
- D. A link between the call, its retrieval, tools and the user's complaint

<details><summary>Answer</summary>

**Answer: D** - One id to join every log.

</details>

### Q3. Average latency is 1.2 s. Why also report p95?

- A. The average hides the slow tail that some users suffer
- B. It's smaller
- C. Customers like percentiles
- D. It's required by law

<details><summary>Answer</summary>

**Answer: A** - p95 shows the experience of the slowest 5%.

</details>

### Q4. The right article was missing from the index. Which stage failed?

- A. Data / ingestion
- B. Model
- C. Prompt
- D. Streaming

<details><summary>Answer</summary>

**Answer: A** - It never reached retrieval.

</details>
