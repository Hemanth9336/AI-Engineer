---
type: scenario
title: "Scenario: how much freedom to give an agent"
minutes: 6
---

Your disk agent works well, and the team wants more: "Let it clean up old files when a disk gets full." Someone proposes adding a tool `run_shell(command: str)` so it can do whatever is needed.

### Q1. What is the main problem with a run_shell tool?

- A. It gives the agent unlimited power - one bad decision or injected instruction can run any command
- B. It is slow
- C. Agents can't use shell tools
- D. It uses too many tokens

<details><summary>Answer</summary>

**Answer: A** - A general shell tool turns every model mistake into a potential outage.

</details>

### Q2. What is a safer design?

- A. run_shell with a warning in the prompt
- B. Remove all tools
- C. Let the agent run as root
- D. A narrow tool like delete_logs_older_than(host, days) with limits, plus human approval before it runs

<details><summary>Answer</summary>

**Answer: D** - Narrow tools, validated arguments, and approval for destructive steps keep the blast radius small.

</details>

### Q3. The agent ran 40 steps on one question and cost a lot. What guard was missing?

- A. A bigger model
- B. Streaming
- C. A longer system prompt
- D. A step limit such as recursion_limit, plus monitoring of tool calls

<details><summary>Answer</summary>

**Answer: D** - Cap the loop and watch the log, so a confused agent stops early.

</details>

### Q4. How should you roll out new agent powers?

- A. All at once to production
- B. Start read-only, log every call, review the logs, then add narrow write actions with approval
- C. Only after the model says it is ready
- D. Never - agents are unsafe

<details><summary>Answer</summary>

**Answer: B** - Earn trust step by step, with evidence from the logs.

</details>
