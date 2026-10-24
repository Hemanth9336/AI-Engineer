---
type: quiz
title: "Quick check: tool calling"
minutes: 6
---

### Q1. Who actually runs the function when a model makes a tool call?

- A. The model provider's servers
- B. The tool runs automatically inside the API
- C. The model itself
- D. Your program

<details><summary>Answer</summary>

**Answer: D** - The model only requests the call. Your code decides whether and how to run it.

</details>

### Q2. What does finish_reason: "tool_calls" tell you?

- A. The reply is complete
- B. The model wants you to run one or more tools and send back the results
- C. The request failed
- D. The model ran out of tokens

<details><summary>Answer</summary>

**Answer: B** - It's waiting for tool results before it can answer.

</details>

### Q3. How does the model know which tool result belongs to which call?

- A. By the order of messages only
- B. By the tool_call_id in the tool message, which matches the call's id
- C. By the tool's name
- D. It guesses

<details><summary>Answer</summary>

**Answer: B** - Each tool message carries the id of the call it answers.

</details>

### Q4. A model calls delete_user with an ID from a customer's email. What should your code do first?

- A. Run it immediately
- B. Validate the arguments and check whether this action needs approval
- C. Ask the model if it is sure
- D. Ignore tool calls

<details><summary>Answer</summary>

**Answer: B** - Tool arguments are untrusted. Check them, and gate destructive actions.

</details>
