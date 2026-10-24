---
type: scenario
title: "Fine-tune on our data so it knows our company"
minutes: 5
---

Kestrel Bank's CTO opens the kick-off: "We have 20,000 internal policy documents. We want you to fine-tune a model on all of them so it knows our company. Then staff can ask it anything."

### Q1. What's the core problem with this plan?

- A. 20,000 documents is too few
- B. Fine-tuning doesn't reliably teach facts: the model would blur policies, invent nearby ones, and couldn't cite where an answer came from
- C. Banks can't fine-tune
- D. It would take too long to type the documents

<details><summary>Answer</summary>

**Answer: B** - Facts belong in retrieval, not weights.

</details>

### Q2. Which follow-up concern matters most for a bank?

- A. The model's name
- B. The number of layers
- C. GPU colour
- D. Permissions and change: a fine-tuned model exposes every document to every user, and a policy change means retraining

<details><summary>Answer</summary>

**Answer: D** - RAG can filter by user and update instantly.

</details>

### Q3. What do you propose?

- A. Refuse the project
- B. Paste all documents into one prompt
- C. Fine-tune and add RAG later if it fails
- D. RAG over the documents with permission filtering and citations, measured on a golden set - and revisit fine-tuning later only for a specific, measured gap

<details><summary>Answer</summary>

**Answer: D** - Solve the knowledge problem with the tool built for it.

</details>
