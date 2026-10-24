---
type: quiz
title: "Quick check: tool calling"
minutes: 3
---

### Q1. Who executes a tool when the model returns a tool call?

- A. Your code
- B. The model provider
- C. The user's browser
- D. Nobody - it's automatic

<details><summary>Answer</summary>

**Answer: A** - The model only proposes; your code decides and runs it.

</details>

### Q2. What must come immediately before a `tool` result message?

- A. A system message
- B. Nothing
- C. A user message
- D. The assistant message containing the matching tool call

<details><summary>Answer</summary>

**Answer: D** - Results must follow the tool call they answer, linked by tool_call_id.

</details>

### Q3. Which part of a tool definition most affects *when* the model calls it?

- A. The description
- B. The name's length
- C. The order of properties
- D. The tool_call_id

<details><summary>Answer</summary>

**Answer: A** - The description is a prompt for tool selection.

</details>

### Q4. The model requests a tool name your code doesn't have. What should happen?

- A. eval() the name
- B. Return an error result like {"error": "unknown tool"} and continue
- C. Crash
- D. Call a random tool

<details><summary>Answer</summary>

**Answer: B** - Fixed dispatch table, errors as results.

</details>
