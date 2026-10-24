---
type: quiz
title: "Quick check: error handling"
minutes: 4
---

### Q1. A tool raises KeyError inside your loop and the run dies with a traceback. What's the harness fix?

- A. Tell the model in the prompt never to pass unknown names
- B. Restart the agent from step 1 automatically
- C. Remove the tool
- D. Catch the exception in run_tool and return it as the tool result

<details><summary>Answer</summary>

**Answer: D** - Errors are information for the model. As a result message, the model can look around and try again.

</details>

### Q2. Which error is worth retrying automatically?

- A. ValueError: days must be 30 or less
- B. TimeoutError from a status API
- C. HTTP 404 Not Found
- D. TypeError: missing argument

<details><summary>Answer</summary>

**Answer: B** - Timeouts are often transient. The others will fail the same way every time.

</details>

### Q3. Why use exponential backoff instead of retrying immediately?

- A. It's required by Python
- B. It avoids the need for a step limit
- C. It makes each attempt cheaper
- D. It gives a struggling service time to recover instead of hammering it

<details><summary>Answer</summary>

**Answer: D** - Immediate retries add load at the worst moment. Waiting longer after each failure helps the service recover.

</details>

### Q4. The model's tool call arguments are '{name: search' (invalid JSON). Where must the harness handle this?

- A. Inside the tool function
- B. In the system prompt
- C. Nowhere - the API guarantees valid JSON
- D. Where the loop parses call.function.arguments, before calling run_tool

<details><summary>Answer</summary>

**Answer: D** - json.loads fails before any tool runs. Catch it there and return an error result for that call.

</details>

### Q5. All three retries of a tool time out. What should the model receive?

- A. Nothing - skip the tool message
- B. An error result like 'error: TimeoutError: status API timed out after 2s'
- C. A fake success so the task can continue
- D. The full Python traceback

<details><summary>Answer</summary>

**Answer: B** - Every call needs a result, and an honest error lets the model choose another path or tell the user.

</details>
