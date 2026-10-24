---
type: quiz
title: "Quick check: the problem RAG solves"
minutes: 5
---

### Q1. You ask a model when your team's on-call rotation changes, and it replies 'Most teams rotate weekly on Mondays'. What happened?

- A. The model looked up your rota
- B. The model is broken
- C. The model guessed - your rota was never in its training data
- D. Your question was too short

<details><summary>Answer</summary>

**Answer: C** - It produced a plausible general answer. The real fact was never inside the model.

</details>

### Q2. What is the most reliable way to get the model to answer with your team's real deploy time?

- A. Ask the question more politely
- B. Ask the same question several times
- C. Use a longer question
- D. Put the document that contains the deploy time in the prompt, then ask

<details><summary>Answer</summary>

**Answer: D** - No prompt can pull out a fact that was never learned. Supplying the document puts the fact in reach.

</details>

### Q3. Why is a confident wrong answer more dangerous than 'I don't know'?

- A. It costs more tokens
- B. It is slower
- C. It looks like a real answer, so it can end up in real decisions
- D. It is not more dangerous

<details><summary>Answer</summary>

**Answer: C** - 'I don't know' stops you; a plausible guess misleads you.

</details>

### Q4. In Retrieval-Augmented Generation, what does the 'retrieval' step do?

- A. Trains the model on your documents
- B. Writes the final answer
- C. Finds the right piece of your documents for the question
- D. Deletes old documents

<details><summary>Answer</summary>

**Answer: C** - Retrieval finds the piece; augmentation adds it to the prompt; generation writes the answer.

</details>
