---
type: quiz
title: "Quick check: choosing your layer"
minutes: 6
---

### Q1. Developers want an agent in their terminal that can use the internal deploy system. Best starting point?

- A. Extend an existing harness with an MCP server and hooks
- B. Write a harness from scratch
- C. Fine-tune a model
- D. A chatbot website

<details><summary>Answer</summary>

**Answer: A** - The missing piece is a tool and a policy, not a loop.

</details>

### Q2. When does an agent SDK fit better than extending Claude Code?

- A. When you have no tools
- B. Never
- C. When you want shell access
- D. When the agent runs inside your own product or service with your UI, auth and storage

<details><summary>Answer</summary>

**Answer: D** - SDKs give you the loop as a library inside your system.

</details>

### Q3. Which is a good reason to build the loop from scratch?

- A. It's more interesting
- B. To use more tools
- C. To avoid writing evals
- D. A hard constraint on every call - audit, latency, call count or runtime - that no layer above meets

<details><summary>Answer</summary>

**Answer: D** - Own the loop when the loop is the constraint.

</details>

### Q4. What do you still own when you extend a production harness?

- A. Nothing
- B. Tools, permissions, instructions, and the evals that prove it works
- C. Only billing
- D. The model weights

<details><summary>Answer</summary>

**Answer: B** - The harness gives you a loop, not a guarantee.

</details>
