---
type: quiz
title: "Quick check: the pipeline"
minutes: 7
---

### Q1. Which phase runs only when documents change?

- A. Retrieve
- B. All three
- C. Generate
- D. Index

<details><summary>Answer</summary>

**Answer: D** - Indexing is the expensive batch step.

</details>

### Q2. Your bot answers correctly but prints 'Sources: costs.md' when the model refused. What's wrong?

- A. Nothing
- B. Sources should be omitted when the answer is a refusal
- C. costs.md should be deleted
- D. k is too small

<details><summary>Answer</summary>

**Answer: B** - Citing chunks that didn't hold the answer misleads the reader.

</details>

### Q3. Why label each chunk with <document source="...">?

- A. To make the prompt longer
- B. So the model and the reader can tell where each fact came from
- C. Because embeddings need it
- D. To hide the source

<details><summary>Answer</summary>

**Answer: B** - Labels keep facts traceable to documents.

</details>

### Q4. What does increasing k from 2 to 8 trade off?

- A. A better chance the right chunk is included, against more noise and cost in every prompt
- B. Nothing
- C. Faster answers
- D. Fewer embedding calls

<details><summary>Answer</summary>

**Answer: A** - Measure it rather than guess - topic 12.

</details>
