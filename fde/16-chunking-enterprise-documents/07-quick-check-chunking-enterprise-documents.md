---
type: quiz
title: "Quick check: chunking enterprise documents"
minutes: 3
---

### Q1. Why not embed a 40-page manual as one vector?

- A. It's too cheap
- B. It's against the API terms
- C. Vectors can't be that long
- D. The meaning averages out, and small embedding models ignore text past their input limit

<details><summary>Answer</summary>

**Answer: D** - One vector can't represent 40 pages of different topics.

</details>

### Q2. What's the best boundary for chunks when the document has headings?

- A. The document's own sections
- B. Every 500 characters
- C. Every sentence
- D. Random

<details><summary>Answer</summary>

**Answer: A** - Authors already grouped related text under headings.

</details>

### Q3. Why prepend 'Shipping Policy - Damage and loss' to a chunk?

- A. To make it longer
- B. To change the id
- C. It's required
- D. So the chunk makes sense alone and the heading words help retrieval

<details><summary>Answer</summary>

**Answer: D** - Context for both the embedding and the model.

</details>

### Q4. 40% of an intranet export is empty template pages. What do you do?

- A. Drop them in cleaning and report the number to the customer
- B. Index them anyway
- C. Fill them with AI text
- D. Ignore the export

<details><summary>Answer</summary>

**Answer: A** - Clean and surface the finding.

</details>
