---
type: quiz
title: "Quick check: RAG on Chroma"
minutes: 6
---

### Q1. You moved retrieval from SQLite to Chroma. Which part of the pipeline must change?

- A. The grounded prompt
- B. The chat model
- C. Only the store and retrieval code
- D. Everything

<details><summary>Answer</summary>

**Answer: C** - Generation still receives (text, source) pairs.

</details>

### Q2. Why should answer() return a dict instead of printing?

- A. Dicts are faster
- B. Chroma requires it
- C. Printing is not allowed
- D. Other code - APIs, bots, eval scripts - can use and test the result

<details><summary>Answer</summary>

**Answer: D** - Structured results are reusable.

</details>

### Q3. A script in /home/app imports your module, which opens PersistentClient(path="db"). What happens?

- A. It opens your db folder
- B. It opens or creates /home/app/db - an empty collection
- C. It raises an error
- D. It downloads the data

<details><summary>Answer</summary>

**Answer: B** - Relative paths follow the current folder; use Path(__file__).

</details>

### Q4. In the Chroma version, who calls lab-embed for the chunks?

- A. Your code, before upsert
- B. The chat model
- C. Nobody
- D. Chroma, through the embedding function, on upsert

<details><summary>Answer</summary>

**Answer: D** - Chroma embeds documents on upsert and questions on query.

</details>
