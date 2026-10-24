---
type: quiz
title: "Quick check: your vector store"
minutes: 5
---

### Q1. You run your indexing script twice. With INSERT OR REPLACE and id as PRIMARY KEY, how many rows do 5 chunks produce?

- A. 10
- B. 5
- C. 0
- D. It depends on the embeddings

<details><summary>Answer</summary>

**Answer: B** - The second run replaces the same IDs - idempotent.

</details>

### Q2. What is the minimum a vector store must keep for each chunk to support RAG?

- A. Only the embedding
- B. The id, the text and the embedding
- C. Only the text
- D. The question history

<details><summary>Answer</summary>

**Answer: B** - Search needs the embedding; the prompt needs the text; updates need the id.

</details>

### Q3. Why does a flat search become a problem at 10 million chunks?

- A. SQLite can't store that many rows
- B. IDs run out
- C. Cosine similarity stops working
- D. It compares the query against every vector on each search

<details><summary>Answer</summary>

**Answer: D** - Approximate indexes like HNSW avoid checking every vector.

</details>

### Q4. At query time, what does query_store.py send to lab-embed?

- A. Every chunk and the question
- B. Only the question
- C. Only the chunks
- D. Nothing

<details><summary>Answer</summary>

**Answer: B** - Chunk vectors were stored at indexing time.

</details>
