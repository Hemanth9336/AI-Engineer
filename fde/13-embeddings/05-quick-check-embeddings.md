---
type: quiz
title: "Quick check: embeddings"
minutes: 4
---

### Q1. What does an embedding represent?

- A. The text compressed for storage
- B. A summary
- C. The number of tokens
- D. The text's meaning as a vector, so similar meanings are close

<details><summary>Answer</summary>

**Answer: D** - Embeddings place similar meanings near each other.

</details>

### Q2. Why can 'my parcel arrived broken' match an article titled 'Reporting a damaged parcel'?

- A. They share many words
- B. Their embeddings are close because the meaning is similar
- C. Luck
- D. The title is short

<details><summary>Answer</summary>

**Answer: B** - Semantic similarity, not keyword overlap.

</details>

### Q3. You embedded the documents with model A. Questions are embedded with model B. What happens?

- A. It works the same
- B. It's faster
- C. Scores are meaningless - vectors from different models aren't comparable
- D. Only the cost changes

<details><summary>Answer</summary>

**Answer: C** - Always use the same embedding model for documents and queries.

</details>

### Q4. Which is the most efficient way to embed 500 short texts?

- A. 500 separate calls
- B. One call per word
- C. Batched calls with many inputs each
- D. Use a chat model

<details><summary>Answer</summary>

**Answer: C** - Batch inputs to cut latency and overhead.

</details>
