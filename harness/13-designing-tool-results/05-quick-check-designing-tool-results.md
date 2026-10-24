---
type: quiz
title: "Quick check: designing tool results"
minutes: 4
---

### Q1. Why is a 400 KB tool result expensive even if the context window can hold it?

- A. It stays in the history and is re-sent - and paid for - on every later step
- B. It's charged as output
- C. Providers charge extra for tool results
- D. It slows down the tool

<details><summary>Answer</summary>

**Answer: A** - Every later request carries it. One careless call taxes the whole rest of the run.

</details>

### Q2. Your tool cuts results at 4,000 characters without saying so. What's the risk?

- A. The model reasons confidently about partial data, not knowing anything is missing
- B. None
- C. The API rejects truncated text
- D. It uses more tokens

<details><summary>Answer</summary>

**Answer: A** - Always mark truncation and say how to get the rest.

</details>

### Q3. Which pagination footer best helps the model?

- A. page 2 of 5 (230 files). Call again with page=3 for more.
- B. More results available.
- C. ...
- D. (truncated)

<details><summary>Answer</summary>

**Answer: A** - It says where it is, how much exists, and the exact next call.

</details>

### Q4. A query produces 18,000 rows the agent may need to process in full. Best pattern?

- A. Write them to a file and return the path, size and columns
- B. Return all rows in the tool result
- C. Return the first 10 rows silently
- D. Refuse the query

<details><summary>Answer</summary>

**Answer: A** - A pointer keeps the context small while keeping the data available to other tools or subagents.

</details>

### Q5. What should a log search tool tell the model besides the matching lines?

- A. How many lines matched in total, how many are shown, and how to narrow the search
- B. Nothing else
- C. The full file path on disk and its permissions
- D. The tool's source code

<details><summary>Answer</summary>

**Answer: A** - Counts and a next-step hint let the model decide whether it has enough.

</details>
