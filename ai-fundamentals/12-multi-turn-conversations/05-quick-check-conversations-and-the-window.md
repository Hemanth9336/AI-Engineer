---
type: quiz
title: "Quick check: conversations and the window"
minutes: 4
---

### Q1. Your second request says 'make it shorter' but the model has no idea what 'it' is. Why?

- A. The request did not include the earlier messages - the API keeps no memory between calls
- B. The model forgot because of its cutoff date
- C. The temperature was too low
- D. The model ran out of tokens

<details><summary>Answer</summary>

**Answer: A** - Each request stands alone; the client must send the history.

</details>

### Q2. What does the context window limit?

- A. The total tokens of the input messages plus the output in one request
- B. Only the length of the reply
- C. How many requests you can make per minute
- D. How many users can share a model

<details><summary>Answer</summary>

**Answer: A** - The window covers everything in one request: input and output together.

</details>

### Q3. A support chat is on turn 60 and each request is getting slow and expensive. What is a good fix?

- A. Switch to a bigger context window and keep sending everything
- B. Set max_tokens to 1
- C. Delete the system message
- D. Summarize the older turns into one message and keep the recent ones

<details><summary>Answer</summary>

**Answer: D** - Summarizing keeps the key facts while cutting input tokens.

</details>

### Q4. Which role holds the model's own earlier replies when you send the history?

- A. system
- B. user
- C. assistant
- D. tool

<details><summary>Answer</summary>

**Answer: C** - Earlier model replies are sent back as assistant messages.

</details>
