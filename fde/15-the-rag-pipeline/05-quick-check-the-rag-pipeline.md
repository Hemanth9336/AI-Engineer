---
type: quiz
title: "Quick check: the RAG pipeline"
minutes: 4
---

### Q1. Why is RAG the default way to make a model use a customer's documents?

- A. It puts the relevant facts in the prompt at question time - current, private and checkable
- B. It retrains the model
- C. It's the only option
- D. It removes the need for a prompt

<details><summary>Answer</summary>

**Answer: A** - No training needed, and answers update as documents do.

</details>

### Q2. A fact is in the PDF, but no chunk contains it. Which stage failed?

- A. Retrieve
- B. Ingest
- C. Generate
- D. Prompt

<details><summary>Answer</summary>

**Answer: B** - The text was lost before indexing.

</details>

### Q3. The right chunk was retrieved and sent, but the answer ignores it. Where do you look next?

- A. Ingest
- B. The embedding model
- C. The prompt that was sent, then the model
- D. The vector store

<details><summary>Answer</summary>

**Answer: C** - Retrieval worked; check the prompt and generation.

</details>

### Q4. What should a grounded RAG system say when retrieval returns irrelevant sources?

- A. Its best guess
- B. A clear 'I don't know'
- C. Nothing
- D. The sources verbatim

<details><summary>Answer</summary>

**Answer: B** - A graceful refusal is the safe failure.

</details>
