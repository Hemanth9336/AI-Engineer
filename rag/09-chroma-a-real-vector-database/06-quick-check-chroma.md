---
type: quiz
title: "Quick check: Chroma"
minutes: 5
---

### Q1. Chroma returns a cosine distance of 0.25 for a hit. What is the cosine similarity?

- A. 0.25
- B. -0.25
- C. 1.25
- D. 0.75

<details><summary>Answer</summary>

**Answer: D** - similarity = 1 - distance.

</details>

### Q2. You run load_chroma.py twice with upsert. What happens to the 5 chunks?

- A. They become 10
- B. They stay 5 - the same IDs are replaced
- C. They are deleted
- D. Chroma raises an error

<details><summary>Answer</summary>

**Answer: B** - upsert inserts or replaces by ID.

</details>

### Q3. Why does query() return [['handbook-000', ...]] - a list inside a list?

- A. It's a bug
- B. query_texts accepts several questions; there is one result list per question
- C. Chroma always duplicates results
- D. For sorting

<details><summary>Answer</summary>

**Answer: B** - Take [0] for a single question.

</details>

### Q4. Your collection was created with the default l2 space. How do you switch it to cosine?

- A. Pass the cosine space when querying
- B. Change the embedding model
- C. Upsert again
- D. Delete and recreate the collection with the cosine space

<details><summary>Answer</summary>

**Answer: D** - The space is fixed at creation time.

</details>
