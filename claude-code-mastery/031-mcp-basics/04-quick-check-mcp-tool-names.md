---
type: quiz
title: "Quick check: MCP tool names"
minutes: 9
---

### Q1. You registered a server called `jira`. What is its search tool called in Claude Code?

- A. jira.search
- B. mcp:jira:search
- C. search@jira
- D. mcp__jira__search

<details><summary>Answer</summary>

**Answer: D** - MCP tools are named mcp__<server>__<tool>.

</details>

### Q2. Which hook matcher catches every tool from the `jira` server?

- A. mcp__jira
- B. jira
- C. mcp__jira__.*
- D. mcp__*

<details><summary>Answer</summary>

**Answer: C** - A bare mcp__jira is an exact name and matches nothing; the regex needs .*

</details>

### Q3. You want the whole team to get the server when they clone the repo. Which scope?

- A. local
- B. user
- C. managed
- D. project

<details><summary>Answer</summary>

**Answer: D** - Project scope writes .mcp.json in the repo.

</details>

### Q4. In a CI job you want only the servers in `ci-mcp.json`, regardless of what is configured on the runner. Flags?

- A. --mcp-config ci-mcp.json --strict-mcp-config
- B. --allowedTools mcp__*
- C. --scope project
- D. --no-mcp

<details><summary>Answer</summary>

**Answer: A** - --strict-mcp-config ignores every other configured server.

</details>
