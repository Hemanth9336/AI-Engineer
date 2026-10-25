---
type: scenario
title: "Scenario: rolling out a remote server to the team"
minutes: 8
---

Your platform team runs an internal HTTP MCP server for deploy status at `https://deploys.internal.example/mcp`. It needs a per-person token. You want every engineer to have it with one `git pull`, and nobody's token in git.

### Q1. What goes in the committed `.mcp.json`?

- A. {"deploys": {"url": "https://deploys.internal.example/mcp"}}
- B. {"deploys": {"type": "http", "url": "https://deploys.internal.example/mcp", "headers": {"Authorization": "Bearer ${DEPLOYS_TOKEN}"}}}
- C. Each engineer's token
- D. Nothing - everyone runs claude mcp add

<details><summary>Answer</summary>

**Answer: B** - Set type explicitly and expand the token from each person's environment.

</details>

### Q2. Ana says Claude still talks to the **old** staging URL after the pull. `claude mcp get deploys` says `Scope: Local config`. Why?

- A. The pull failed
- B. SSE fallback
- C. Her local-scope entry with the same name wins over the project one
- D. Tool search

<details><summary>Answer</summary>

**Answer: C** - Local beats project; she should remove her local entry.

</details>

### Q3. New hires see `Pending approval` for deploys. Is that a bug?

- A. Yes
- B. It means the token is wrong
- C. Only on Linux
- D. No - servers from a repository's .mcp.json need each person's approval, and a trusted folder

<details><summary>Answer</summary>

**Answer: D** - A cloned repo can't approve its own servers; each person approves once.

</details>

### Q4. The `list_deploys` tool returns 3 MB of JSON and Claude says the result was saved to a file. Best fix?

- A. Raise MAX_MCP_OUTPUT_TOKENS to the maximum
- B. Switch to SSE
- C. Add filters and paging to the tool so it returns what a question needs
- D. Disable tool search

<details><summary>Answer</summary>

**Answer: C** - Large outputs cost context; make the tool return less.

</details>
