---
type: quiz
title: "Quick check: MCP"
minutes: 4
---

### Q1. What problem does MCP solve?

- A. Model training cost
- B. Token limits
- C. Every AI app needing its own integration with every system - write a server once, use it from any MCP client
- D. Hallucinations

<details><summary>Answer</summary>

**Answer: C** - One standard interface between AI clients and tools.

</details>

### Q2. Why must a stdio MCP server never print to stdout?

- A. It's slow
- B. Stdout is the protocol channel - stray text corrupts the messages
- C. Clients ignore stdout
- D. It leaks keys

<details><summary>Answer</summary>

**Answer: B** - Log to a file or stderr instead.

</details>

### Q3. How does FastMCP know a tool's description and parameters?

- A. From a YAML file
- B. It asks the model
- C. From the function's docstring and type hints
- D. From the server name

<details><summary>Answer</summary>

**Answer: C** - Docstring for the description, type hints for the schema.

</details>

### Q4. In claude -p, why pass --allowedTools mcp__meridian__track_parcel instead of allowing everything?

- A. Least privilege - only the tool the task needs can run without a prompt
- B. It's faster
- C. It's required syntax
- D. To save tokens

<details><summary>Answer</summary>

**Answer: A** - Allow exactly what's needed.

</details>
