---
type: quiz
title: "Quick check: extending with MCP"
minutes: 4
---

### Q1. What does Claude Code name the `incident_status` tool from a server called `opsdesk`?

- A. incident_status
- B. opsdesk.incident_status
- C. mcp__opsdesk__incident_status
- D. tool:incident_status

<details><summary>Answer</summary>

**Answer: C** - The prefix keeps tools from different servers apart.

</details>

### Q2. Which scope writes `.mcp.json` into the repository for the whole team?

- A. project
- B. local
- C. user
- D. global

<details><summary>Answer</summary>

**Answer: A** - Commit `.mcp.json`; teammates approve it on first use.

</details>

### Q3. Why does a CI job pass `--mcp-config ci-mcp.json --strict-mcp-config`?

- A. It's faster
- B. It's required for stdio servers
- C. It disables permissions
- D. Only the listed servers load - the run doesn't depend on whatever a machine has registered

<details><summary>Answer</summary>

**Answer: D** - Reproducible tool sets make reproducible runs.

</details>

### Q4. Your server's tool returns the full incident record, including internal notes. What's wrong?

- A. Nothing
- B. Results go into the model's context - return only what the model needs (topic 13)
- C. MCP forbids dicts
- D. It's too slow

<details><summary>Answer</summary>

**Answer: B** - Shape results; the harness won't do it for you.

</details>

### Q5. Why must a stdio MCP server never print to stdout?

- A. It's slow
- B. stdout carries the protocol messages - stray text corrupts them
- C. Clients ignore it
- D. It leaks keys

<details><summary>Answer</summary>

**Answer: B** - Log to a file or stderr.

</details>
