---
type: quiz
title: "Quick check: evaluating RAG"
minutes: 6
---

### Q1. Retrieval hit rate is 100% but answer accuracy is 60%. Where should you look first?

- A. Generation - the prompt rules or the model
- B. The chunk size
- C. The embedding model
- D. The eval set is broken

<details><summary>Answer</summary>

**Answer: A** - The right chunks arrive; the model isn't using them well.

</details>

### Q2. Why include questions the documents can't answer?

- A. To measure whether the bot refuses instead of inventing an answer
- B. To make the score lower
- C. Because retrieval needs them
- D. They aren't useful

<details><summary>Answer</summary>

**Answer: A** - 'Knows its limits' is a behaviour you must test.

</details>

### Q3. An item expects '35 days'. The answer is 'Backups are kept for 35 Days.' With your rules it is:

- A. Wrong - the case differs
- B. Half correct
- C. Skipped
- D. Correct - matching ignores case

<details><summary>Answer</summary>

**Answer: D** - Both sides are lower-cased before comparing.

</details>

### Q4. Which eval needs no chat-model calls?

- A. Answer accuracy
- B. Both
- C. Retrieval hit rate
- D. Neither

<details><summary>Answer</summary>

**Answer: C** - Retrieval eval only queries the vector store.

</details>
