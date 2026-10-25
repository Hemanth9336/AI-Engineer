---
type: quiz
title: "Quick check: the wrapper that lied"
minutes: 11
---

### Q1. A wrapper reruns the agent until its final message contains "all tests pass". It reports success on a broken build. Why?

- A. The model is bad
- B. The success signal is the agent's own claim; nothing independent was checked
- C. It needed more attempts
- D. grep is case sensitive

<details><summary>Answer</summary>

**Answer: B** - Verify with your own command; the agent's summary is not evidence.

</details>

### Q2. Verification fails on attempt 1. What should attempt 2's prompt contain?

- A. What failed and the tail of the verifier's output, sent with --resume to the same session
- B. "Try again"
- C. The whole task again in a new session
- D. Nothing; just rerun

<details><summary>Answer</summary>

**Answer: A** - Evidence plus context turns a retry into a correction.

</details>

### Q3. Attempt 2 passes because the agent deleted the failing assertion. How should the wrapper have caught it?

- A. It can't
- B. Use plan mode
- C. Deny Edit/Write on tests/ and compare a hash of tests/ after every attempt, failing and restoring on any change
- D. Run the tests twice

<details><summary>Answer</summary>

**Answer: C** - A verifier the agent can edit isn't independent.

</details>

### Q4. The envelope says `is_error: true` but your tests pass anyway. Success or failure?

- A. Failure - the run didn't complete normally, so its edits may be partial; count it as a failed attempt
- B. Success
- C. Ignore is_error
- D. Depends on cost

<details><summary>Answer</summary>

**Answer: A** - Both the run and the verification must succeed.

</details>

### Q5. A task needs 3 attempts on most nights. What do the logs tell you to do?

- A. Look at why attempt 1 fails - the prompt, the context, or the tests - and fix that, since retries cost time and money
- B. Raise the limit to 10
- C. Nothing
- D. Switch to opus

<details><summary>Answer</summary>

**Answer: A** - attempts.jsonl turns flakiness into something you can measure and fix.

</details>
