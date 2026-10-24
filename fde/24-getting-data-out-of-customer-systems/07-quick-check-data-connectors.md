---
type: quiz
title: "Quick check: data connectors"
minutes: 3
---

### Q1. Order status changes every few minutes. How should the assistant get it?

- A. Call the orders API as a tool at question time
- B. Index it nightly
- C. Fine-tune on it
- D. Ask the user

<details><summary>Answer</summary>

**Answer: A** - Fast-changing data belongs behind a tool, not in an index.

</details>

### Q2. What two things does a source need to support incremental sync?

- A. A CSV and a PDF
- B. An API key and a webhook
- C. A vector database and a GPU
- D. A stable id per record and a change marker such as updated_at

<details><summary>Answer</summary>

**Answer: D** - Ids to match records, markers to detect changes.

</details>

### Q3. A policy is withdrawn in the source but still appears in answers. What was missed?

- A. Embedding the update
- B. A higher k
- C. A bigger chunk size
- D. Handling deletes in the sync

<details><summary>Answer</summary>

**Answer: D** - Forgotten deletes keep stale content retrievable.

</details>

### Q4. A sync run would remove 90% of the index. What should happen?

- A. Apply it
- B. Delete the rest too
- C. Re-run until it works
- D. Stop and check - it's more likely a broken export than a mass deletion

<details><summary>Answer</summary>

**Answer: D** - Large unexpected changes need a human check.

</details>
