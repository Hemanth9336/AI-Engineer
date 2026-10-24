---
type: quiz
title: "Quick check: RAG with LangChain"
minutes: 6
---

### Q1. What does a LangChain retriever return when you invoke it with a question?

- A. An answer string
- B. A list of Document objects
- C. Embeddings
- D. A prompt

<details><summary>Answer</summary>

**Answer: B** - Retrievers return Documents; the chain formats them into the prompt.

</details>

### Q2. Why set check_embedding_ctx_length=False on OpenAIEmbeddings for lab-embed?

- A. Otherwise it sends OpenAI token IDs, which non-OpenAI models don't accept
- B. To make it faster
- C. To disable embeddings
- D. It's required by Chroma

<details><summary>Answer</summary>

**Answer: A** - The lab model expects text input.

</details>

### Q3. In {"context": retriever | format_docs, "question": RunnablePassthrough()}, what does RunnablePassthrough do?

- A. Deletes the question
- B. Passes the input question through unchanged
- C. Calls the model
- D. Retrieves documents

<details><summary>Answer</summary>

**Answer: B** - Both branches receive the same input; one transforms it, one passes it on.

</details>

### Q4. Your RecursiveCharacterTextSplitter chunks start at headings, but your own chunker cut mid-word. Why does that matter for retrieval?

- A. Topic-aligned chunks give sharper vectors, so matching questions score higher
- B. It doesn't
- C. Headings are removed
- D. It makes the index smaller

<details><summary>Answer</summary>

**Answer: A** - The vacation question rose from 0.50 to 0.70 with the same model.

</details>
