---
type: quiz
title: "Quick check: vector search"
minutes: 4
---

### Q1. What does a vector store record need for citations and updates?

- A. Only the embedding
- B. The query
- C. Only the text
- D. A stable id, plus the text and embedding

<details><summary>Answer</summary>

**Answer: D** - Ids make citations, updates and deletes possible.

</details>

### Q2. Top results all score low and close together. What does that suggest?

- A. Probably nothing in the store answers the question
- B. Perfect matches
- C. The model is broken
- D. k is too small

<details><summary>Answer</summary>

**Answer: A** - Flat low scores are a classic 'not found' signal.

</details>

### Q3. 'Can we get DDP?' misses the one article that mentions DDP. What usually fixes this?

- A. A bigger chat model
- B. Hybrid search that adds keyword matching
- C. Higher temperature
- D. Fewer documents

<details><summary>Answer</summary>

**Answer: B** - Exact codes and abbreviations need keyword signals.

</details>

### Q4. An answer is wrong. What do you check first?

- A. Whether the right chunk was in the retrieved top-k
- B. The temperature
- C. The model name
- D. The API key

<details><summary>Answer</summary>

**Answer: A** - Split retrieval failures from generation failures.

</details>
