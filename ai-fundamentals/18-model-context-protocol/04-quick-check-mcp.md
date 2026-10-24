---
type: quiz
title: "Quick check: MCP"
minutes: 6
---

### Q1. What problem does MCP solve?

- A. It makes models smarter
- B. It replaces REST APIs
- C. It gives one standard way to connect AI clients to tools and data, so a connector works everywhere
- D. It stores API keys securely

<details><summary>Answer</summary>

**Answer: C** - Write a server once, use it from any MCP client.

</details>

### Q2. You want every engineer who clones the repo to get the same MCP servers. Which scope?

- A. local
- B. user
- C. global
- D. project

<details><summary>Answer</summary>

**Answer: D** - Project scope writes .mcp.json in the repo, which is committed and shared.

</details>

### Q3. Why use 'Authorization: Bearer ${GITHUB_PAT}' in single quotes when adding the server?

- A. Single quotes make the request faster
- B. So the shell keeps the placeholder literal and the real token never lands in .mcp.json
- C. GitHub requires single quotes
- D. To hide the URL

<details><summary>Answer</summary>

**Answer: B** - Double quotes would expand the variable and save your token in a committed file.

</details>

### Q4. A random repo you cloned has a .mcp.json with an unknown server. What should you do?

- A. Approve it - it came with the repo
- B. Review what the server is and who publishes it before approving it
- C. Delete the repo
- D. Run claude --dangerously-skip-permissions

<details><summary>Answer</summary>

**Answer: B** - MCP servers can see and do a lot. Only approve servers you trust.

</details>
