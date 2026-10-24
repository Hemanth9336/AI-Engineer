---
type: quiz
title: "Quick check: retrieval quality"
minutes: 3
---

### Q1. Which queries are most likely to defeat pure vector search?

- A. Long natural questions
- B. Short polite greetings
- C. Questions about common topics
- D. Queries with codes, abbreviations or rare names

<details><summary>Answer</summary>

**Answer: D** - Exact strings carry little semantic signal.

</details>

### Q2. Why does reciprocal rank fusion combine ranks instead of scores?

- A. Vector and keyword scores are on different scales; ranks need no calibration
- B. Ranks are cheaper
- C. Scores are secret
- D. It's required by BM25

<details><summary>Answer</summary>

**Answer: A** - RRF sidesteps score normalisation.

</details>

### Q3. The model's reranking includes an id that wasn't a candidate. What should the code do?

- A. Use it
- B. Crash
- C. Drop it and keep a reordering of the real candidates
- D. Retry forever

<details><summary>Answer</summary>

**Answer: C** - Defensive merging keeps the output valid.

</details>

### Q4. When is reranking worth keeping?

- A. Always
- B. When it measurably improves hit rate on your test set
- C. Never
- D. Only for small documents

<details><summary>Answer</summary>

**Answer: B** - It costs latency and tokens - it must earn its place.

</details>
