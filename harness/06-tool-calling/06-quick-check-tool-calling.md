---
type: quiz
title: "Quick check: tool calling"
minutes: 4
---

### Q1. Who executes a tool when the model returns a tool call?

- A. Your harness code
- B. The model provider's servers
- C. The model itself, inside its context
- D. The gateway

<details><summary>Answer</summary>

**Answer: A** - The model only proposes the call. Your code decides whether to run it and what to send back.

</details>

### Q2. What must come immediately before a role 'tool' message in the history?

- A. The assistant message that contains the matching tool call
- B. The user's question
- C. A system message
- D. Nothing - tool messages can go anywhere

<details><summary>Answer</summary>

**Answer: A** - The API links each result to a call by tool_call_id, and rejects results that don't follow a matching assistant tool call.

</details>

### Q3. The model asks for read_file with a path that doesn't exist. What should the harness do?

- A. Crash so the developer notices
- B. Retry the same call ten times
- C. Silently return an empty string
- D. Return an error string as the tool result so the model can react

<details><summary>Answer</summary>

**Answer: D** - Errors are information. Returned as a result, the model can try another path or tell the user.

</details>

### Q4. call.function.arguments is...

- A. a Python dict
- B. the tool's return value
- C. always valid
- D. a JSON string the model generated, which you must parse and validate

<details><summary>Answer</summary>

**Answer: D** - It's model output like any other: parse it with json.loads and check it before using it.

</details>

### Q5. Why do this skill's checkers run your harness against labmock instead of a real model?

- A. labmock is smarter
- B. It's required by the OpenAI SDK
- C. Real models can't call tools
- D. A scripted model gives the same replies every run, so harness behavior can be tested deterministically

<details><summary>Answer</summary>

**Answer: D** - To test the harness, you hold the model constant. labmock replays a script through the same API, so your code runs unchanged.

</details>
