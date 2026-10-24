---
type: quiz
title: "Quick check: embeddings"
minutes: 6
---

### Q1. What does an embedding model return for a sentence?

- A. A summary of the sentence
- B. The sentence translated
- C. A fixed-length list of numbers representing its meaning
- D. A yes/no answer

<details><summary>Answer</summary>

**Answer: C** - Embedding models output vectors, not text.

</details>

### Q2. You have 500 texts to embed. What is the best approach?

- A. 500 separate requests
- B. Concatenate them into one string
- C. Send them in batches as a list in input
- D. Embed only the first 10

<details><summary>Answer</summary>

**Answer: C** - Batching is far faster; one vector comes back per input, in order.

</details>

### Q3. You switch from lab-embed to a different embedding model. What must you do with your stored vectors?

- A. Re-embed all your texts with the new model
- B. Nothing
- C. Round them
- D. Normalise them again

<details><summary>Answer</summary>

**Answer: A** - Each model has its own space - vectors from two models can't be compared.

</details>

### Q4. A short sentence and a long paragraph are both embedded with lab-embed. How long are the vectors?

- A. The paragraph's is longer
- B. It depends on the temperature
- C. One number per word
- D. Both are 384 numbers

<details><summary>Answer</summary>

**Answer: D** - The model always returns the same number of dimensions.

</details>
