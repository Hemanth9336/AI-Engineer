---
type: quiz
title: "Quick check: permissions-aware retrieval"
minutes: 4
---

### Q1. Where must document permissions be enforced in a RAG system?

- A. In the system prompt
- B. After the answer is generated
- C. In the UI only
- D. In retrieval, before documents reach the model

<details><summary>Answer</summary>

**Answer: D** - Only documents the user may read should ever be retrieved.

</details>

### Q2. Why filter before ranking rather than after?

- A. It's faster to write
- B. Ranking needs permissions
- C. Filtering the top-k afterwards can leave too few results or none
- D. No difference

<details><summary>Answer</summary>

**Answer: C** - Filter first, then take the top-k of what's visible.

</details>

### Q3. The identity service is down. What should search do?

- A. Show everything
- B. Ask the user their groups
- C. Use yesterday's user list
- D. Fail closed - refuse or return nothing

<details><summary>Answer</summary>

**Answer: D** - Never fall back to open access.

</details>

### Q4. Why is this bug often missed in demos?

- A. Demos are short
- B. Demo users are usually admins who can see everything
- C. Models hide it
- D. Vector stores block it

<details><summary>Answer</summary>

**Answer: B** - Test with real, restricted users.

</details>
