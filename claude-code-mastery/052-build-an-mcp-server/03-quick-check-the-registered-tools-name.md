---
type: quiz
title: "Quick check: the registered tool's name"
minutes: 11
---

### Q1. You registered `claude mcp add wordcount -- python3 server.py`, and the server lists a tool `count_words`. What do you put in `--allowedTools`?

- A. mcp__wordcount__count_words
- B. wordcount.count_words
- C. count_words
- D. mcp:wordcount:count_words

<details><summary>Answer</summary>

**Answer: A** - MCP tools are named mcp__<server>__<tool>, using the name you registered, not the serverInfo name.

</details>

### Q2. The server prints `Server starting on stdio` to stdout before the loop. What happens?

- A. Nothing
- B. It shows in /mcp
- C. The client reads a non-JSON line and the connection fails
- D. It's logged as a warning

<details><summary>Answer</summary>

**Answer: C** - Over stdio, stdout is the protocol channel. Log to stderr.

</details>

### Q3. `tools/call` gets `{"text": 42}`. Which reply helps Claude most?

- A. A result with isError: true and a message saying text must be a string
- B. error -32602
- C. No reply
- D. error -32700

<details><summary>Answer</summary>

**Answer: A** - Claude reads tool results and can retry with corrected arguments; protocol errors look like a broken server.

</details>

### Q4. A request without `id` arrives: `{"jsonrpc":"2.0","method":"notifications/initialized"}`. What should the server send?

- A. {"result": {}}
- B. Nothing
- C. An error
- D. The tool list

<details><summary>Answer</summary>

**Answer: B** - Notifications never get a response.

</details>

### Q5. A deny rule should block only this tool for everyone in the repo. What do you write?

- A. "deny": ["count_words"]
- B. --disallowedTools wordcount
- C. Remove it from .mcp.json
- D. "deny": ["mcp__wordcount__count_words"] in .claude/settings.json

<details><summary>Answer</summary>

**Answer: D** - Permission rules use the same mcp__server__tool name; mcp__wordcount alone would match every tool on the server.

</details>
