---
type: quiz
title: "Quick check: a tool reply that arrives truncated"
minutes: 8
---

### Q1. An MCP tool's result shows a short note with a file path instead of the data. What happened?

- A. The result was over the size limit, so Claude Code saved it to a file under tool-results/ and gave Claude the path
- B. The server crashed
- C. The network dropped
- D. Tool search deferred it

<details><summary>Answer</summary>

**Answer: A** - Large successful results are persisted to disk and referenced.

</details>

### Q2. Which variable raises the token limit for MCP tool results?

- A. MCP_TIMEOUT
- B. ENABLE_TOOL_SEARCH
- C. MAX_MCP_OUTPUT_TOKENS
- D. CLAUDE_CODE_MAX_OUTPUT_TOKENS

<details><summary>Answer</summary>

**Answer: C** - MAX_MCP_OUTPUT_TOKENS defaults to 25,000.

</details>

### Q3. You maintain the server. How do you let one schema tool return up to 200,000 characters inline?

- A. Tell users to set an env var
- B. Set _meta["anthropic/maxResultSizeChars"] on that tool
- C. Use WebSocket
- D. Split it into 4 tools

<details><summary>Answer</summary>

**Answer: B** - The per-tool annotation raises that tool's threshold, up to 500,000 characters.

</details>

### Q4. A remote server's JSON entry has `url` but no `type`. What happens?

- A. It defaults to http
- B. It is treated as stdio and skipped with a configuration error
- C. It defaults to sse
- D. It works

<details><summary>Answer</summary>

**Answer: B** - Always set type: http, sse, or ws.

</details>
