---
type: quiz
title: "Quick check: tool sets"
minutes: 4
---

### Q1. Why can adding more tools make an agent worse?

- A. Tools slow down the API
- B. More overlapping options mean more wrong picks, and every definition is paid for on every step
- C. Models ignore all tools past the fifth
- D. It doesn't - more tools are always better

<details><summary>Answer</summary>

**Answer: B** - Accuracy and cost both degrade as the set grows, especially with near-duplicates.

</details>

### Q2. A tool takes action='status'|'restart'|'delete'. Why split it?

- A. Shorter names
- B. The API limits parameters
- C. The jobs have different risk, and only separate tools can be gated separately
- D. Splitting reduces tokens

<details><summary>Answer</summary>

**Answer: C** - You want status checks free and restarts or deletes gated - that needs separate tools.

</details>

### Q3. get_customer takes customer_id but list_invoices takes user_id for the same value. What's the problem?

- A. Nothing
- B. The API rejects different names
- C. It's a security hole
- D. Inconsistent vocabulary makes the model guess which name means what; use one name per concept

<details><summary>Answer</summary>

**Answer: D** - Consistent names make the tool set read like one design.

</details>

### Q4. A product really needs 60 capabilities. What's a good harness pattern?

- A. Load a small, task-specific set per request - via routing, specialist agents or subagents
- B. Expose all 60 tools in every call
- C. Give the model a list in the system prompt
- D. Pick the 10 most popular and drop the rest

<details><summary>Answer</summary>

**Answer: A** - The product reaches everything; each request only sees what it needs.

</details>
