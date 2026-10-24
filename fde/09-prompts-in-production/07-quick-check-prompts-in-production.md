---
type: quiz
title: "Quick check: prompts in production"
minutes: 4
---

### Q1. Why give the out-of-scope refusal a fixed exact sentence?

- A. It sounds friendlier
- B. Code and evals can reliably detect it
- C. It's cheaper
- D. Models require it

<details><summary>Answer</summary>

**Answer: B** - Exact phrases are machine-checkable.

</details>

### Q2. You need to change the production prompt. What's the right process?

- A. Edit v2.txt in place
- B. Change it in the code only
- C. Delete old versions
- D. Create v3.txt, test it, then point current at v3

<details><summary>Answer</summary>

**Answer: D** - Released versions are immutable; current moves.

</details>

### Q3. Why log the prompt version with every request?

- A. To save tokens
- B. For billing
- C. The API needs it
- D. To know exactly which prompt produced a given answer

<details><summary>Answer</summary>

**Answer: D** - Debugging and audits depend on it.

</details>

### Q4. Why pin a dated model version instead of a 'latest' alias?

- A. Aliases are slower
- B. Aliases expire daily
- C. Dated versions are free
- D. Behaviour can change under you when the alias moves

<details><summary>Answer</summary>

**Answer: D** - Pinning prevents silent behaviour changes.

</details>
