---
type: scenario
title: "A from-scratch harness for a solved problem"
minutes: 5
---

Your platform team wants an agent that helps engineers investigate incidents from their terminal: read logs, query the incident tracker, look at recent deploys, and suggest a fix. Everyone already uses Claude Code. A senior engineer proposes a three-month project: "We'll write our own harness - loop, tools, permissions, compaction - so we control everything."

### Q1. What do you recommend?

- A. Build it from scratch as proposed
- B. Build a chat website instead
- C. Extend Claude Code: MCP servers for the incident tracker and deploy history, hooks for policy, a skill for the investigation workflow
- D. Fine-tune a model first

<details><summary>Answer</summary>

**Answer: C** - The users, interface and task type match an existing harness; what's missing is tools and rules.

</details>

### Q2. What does the from-scratch plan spend most of its three months on?

- A. Re-building the loop, permissions, compaction and terminal UX that already exist
- B. The incident tools
- C. Evals
- D. Talking to users

<details><summary>Answer</summary>

**Answer: A** - The undifferentiated parts dominate the work.

</details>

### Q3. Which part of the work is the same whichever layer you choose?

- A. Writing a streaming parser
- B. Designing the incident tools, the permission policy and an eval suite
- C. Implementing compaction
- D. Building a terminal UI

<details><summary>Answer</summary>

**Answer: B** - Tools, policy and evals are your job in every layer.

</details>

### Q4. What would change your recommendation toward building your own?

- A. The team likes Python
- B. The project sounds more fun
- C. A hard requirement the existing harness can't meet - e.g. it must run inside a locked-down service with every token audited
- D. A bigger budget

<details><summary>Answer</summary>

**Answer: C** - Build when a real constraint rules out the existing layers.

</details>
