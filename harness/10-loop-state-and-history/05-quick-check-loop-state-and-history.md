---
type: quiz
title: "Quick check: loop state and history"
minutes: 4
---

### Q1. Where does an agent's 'memory' of earlier steps live?

- A. In the model's weights
- B. In the provider's session store
- C. In the messages list your harness re-sends on every call
- D. In the tool definitions

<details><summary>Answer</summary>

**Answer: C** - The model is stateless. The history list is the memory - and the harness owns it.

</details>

### Q2. An assistant message contains two tool calls. What must follow it?

- A. One tool message with both results
- B. Two tool messages, one per call id, before any other message
- C. A user message, then the results
- D. Nothing - results are optional

<details><summary>Answer</summary>

**Answer: B** - Each call id needs its own tool message, immediately after the assistant message.

</details>

### Q3. Why convert SDK message objects to plain dicts before appending?

- A. The API requires dicts
- B. Objects can't hold tool calls
- C. Dicts use fewer tokens
- D. So the history can be saved as JSON, reloaded, diffed and replayed

<details><summary>Answer</summary>

**Answer: D** - JSON-serializable history is what makes logging, resume and replay possible.

</details>

### Q4. A 'keep the last 10 messages' trimmer causes 'tool_calls must be followed by tool messages' errors. Why?

- A. 10 is too few
- B. Tool messages can't be trimmed
- C. The model can't handle trimmed histories
- D. It sometimes cuts between an assistant tool call and its results

<details><summary>Answer</summary>

**Answer: D** - Trimming must drop whole turns - an assistant message together with all of its tool results.

</details>

### Q5. A crash lost the result for one read-only tool call. What's the best repair?

- A. Invent a plausible result
- B. Change the tool_call_id to match another result
- C. Delete the assistant message and everything after it
- D. Re-run that read-only call and insert its real result (or an honest error message)

<details><summary>Answer</summary>

**Answer: D** - Real data or an honest error keeps the model grounded. Never fabricate a tool result.

</details>
