---
type: quiz
title: "Quick check: semantic search"
minutes: 6
---

### Q1. A user searches 'app keeps dying'. Why does semantic search find 'The mobile app crashes...' when keyword search doesn't?

- A. It compares meaning via embeddings, not shared words
- B. It ignores the query
- C. It uses a bigger index
- D. It searches the web

<details><summary>Answer</summary>

**Answer: A** - 'dying' and 'crashes' are different words with close meaning.

</details>

### Q2. Which query is keyword search likely BETTER at?

- A. 'my order never came'
- B. 'I want my money back'
- C. 'error E-4012 on checkout'
- D. 'the site is sluggish'

<details><summary>Answer</summary>

**Answer: C** - Exact codes carry no generalisable meaning - exact matching wins.

</details>

### Q3. In a search over 1,000 fixed documents, what should be embedded for each new query?

- A. All 1,000 documents and the query
- B. Only the query - the document vectors are reused
- C. Nothing
- D. Only the top 3 documents

<details><summary>Answer</summary>

**Answer: B** - Candidate vectors don't change; embed them once.

</details>

### Q4. Why return the top 3-5 results rather than only the best one?

- A. It is faster
- B. It gives the next step room - the answer is likely among several pieces
- C. Models need exactly 5
- D. It is required by cosine similarity

<details><summary>Answer</summary>

**Answer: B** - Top-k improves the chance the right piece is included.

</details>
