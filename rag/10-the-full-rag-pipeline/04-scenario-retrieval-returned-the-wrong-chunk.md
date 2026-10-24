---
type: scenario
title: "Scenario: retrieval returned the wrong chunk"
minutes: 6
---

A teammate's RAG bot answers "How long are backups kept?" with "I don't know based on the documents." - but `backups.md` clearly says 35 days. They print the retrieved chunks and see `deploys.md` and `access.md`. The prompt and the model are fine.

### Q1. Where is the problem?

- A. The model is too small
- B. The refusal rule is too strict
- C. Retrieval - the right chunk never reached the prompt
- D. The temperature is too low

<details><summary>Answer</summary>

**Answer: C** - Generation can only use what retrieval gives it. Debug retrieval first.

</details>

### Q2. What is the first thing to check?

- A. Remove the grounding rules
- B. Switch to lab-smart
- C. Whether backups.md was indexed at all - count chunks by source in the store
- D. Increase max_tokens

<details><summary>Answer</summary>

**Answer: C** - A missing or stale index is the most common cause.

</details>

### Q3. backups.md is indexed. Its score for the question is 0.21; the top two score 0.24 and 0.22. What helps?

- A. Ask the question in capital letters
- B. Lower the temperature
- C. Increase k so more chunks are included, and look at how the document is chunked
- D. Delete the other documents

<details><summary>Answer</summary>

**Answer: C** - Bigger k gives retrieval more room; better chunking gives sharper vectors.

</details>

### Q4. How do you stop this from happening silently next time?

- A. Hope
- B. Keep an eval set of questions with known sources and measure retrieval regularly
- C. Turn off refusals
- D. Use a longer system prompt

<details><summary>Answer</summary>

**Answer: B** - Topic 12: measure retrieval with a small eval set.

</details>
