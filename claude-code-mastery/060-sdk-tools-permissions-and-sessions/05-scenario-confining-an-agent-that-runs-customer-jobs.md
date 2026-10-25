---
type: scenario
title: "Scenario: confining an agent that runs customer jobs"
minutes: 7
---

Your support team wants an SDK agent that customers can talk to about their batch jobs. The first prototype gives it `Bash` and `psql` credentials, with `allowed_tools=["Bash(psql *)"]`, "so it can look things up".

### Q1. What's the core problem with the prototype?

- A. psql is slow
- B. Nothing, if the prompt is good
- C. Bash needs a sandbox flag
- D. The agent's real capability is any SQL on any customer's data; the prompt is the only thing keeping it to one customer

<details><summary>Answer</summary>

**Answer: D** - A capability you hand over is a capability a confused or manipulated model can use.

</details>

### Q2. What's the better shape?

- A. A longer system prompt
- B. A read-only database user
- C. Narrow @tool functions (list_jobs, cancel_job) that take the customer from your code, plus can_use_tool checking ownership
- D. Run it in plan mode

<details><summary>Answer</summary>

**Answer: C** - Tools scoped by your code mean a manipulated model still can't reach another tenant.

</details>

### Q3. A teammate adds `allowed_tools=["mcp__jobs__cancel_job"]` "to stop the permission errors". What happens?

- A. Cancels are auto-approved and the ownership check in can_use_tool never runs
- B. Nothing changes
- C. The tool disappears
- D. The SDK refuses to start

<details><summary>Answer</summary>

**Answer: A** - Allow rules are checked before the callback; keep gated tools out of them.

</details>

### Q4. Where should the customer id come from?

- A. The model's tool arguments
- B. An environment variable the agent can read
- C. The prompt
- D. Your server's authenticated session, closed over when the tools and gate are built

<details><summary>Answer</summary>

**Answer: D** - Never let the model choose whose data it acts on.

</details>

### Q5. Compliance wants a record of every tool call, including ones that were blocked. Which mechanism?

- A. A PreToolUse hook - it runs for every call before any permission decision
- B. can_use_tool
- C. The ResultMessage
- D. The session transcript only

<details><summary>Answer</summary>

**Answer: A** - Hooks see auto-approved calls too; callbacks see only the ones that reach them.

</details>
