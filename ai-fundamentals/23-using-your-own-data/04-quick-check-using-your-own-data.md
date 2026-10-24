---
type: quiz
title: "Quick check: using your own data"
minutes: 6
---

### Q1. Why does a model hallucinate about your internal service?

- A. It is broken
- B. It has never seen your internal documents, so it generates something plausible
- C. The temperature is 0
- D. The API is slow

<details><summary>Answer</summary>

**Answer: B** - Private knowledge isn't in its training data - you have to supply it.

</details>

### Q2. What does the 'R' in RAG do?

- A. Repeats the question
- B. Retrieves the most relevant chunks of your documents for each question
- C. Rewrites the answer
- D. Rates the model

<details><summary>Answer</summary>

**Answer: B** - Retrieval selects what goes into the grounding prompt.

</details>

### Q3. What is an embedding?

- A. A compressed copy of a document
- B. An encrypted key
- C. A type of prompt
- D. A list of numbers representing the meaning of a text, so similar texts are close together

<details><summary>Answer</summary>

**Answer: D** - Embeddings let you search by meaning, not just exact words.

</details>

### Q4. Users get confident wrong answers when the docs don't cover a question. What fixes it?

- A. Bigger chunks
- B. An explicit 'not found' reply in the grounding prompt, checked by your code
- C. More temperature
- D. Removing the documents

<details><summary>Answer</summary>

**Answer: B** - Give the model a way out, and handle it in code.

</details>
