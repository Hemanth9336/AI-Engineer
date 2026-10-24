---
type: quiz
title: "Quick check: the API call"
minutes: 3
---

### Q1. In an OpenAI-style chat completion response, where is the reply text?

- A. `.reply`
- B. `.choices[0].message.content`
- C. `.messages[0].content`
- D. `.usage.text`

<details><summary>Answer</summary>

**Answer: B** - Responses can hold several choices; the first one's message content is the text. `messages` is what you sent, not what came back.

</details>

### Q2. Why does the request use `-H "Authorization: Bearer $LAB_AI_KEY"` instead of the key typed out?

- A. It is faster
- B. The gateway rejects typed keys
- C. The key stays out of your shell history, scripts, and files - it is read from the environment at run time
- D. Environment variables are encrypted on disk

<details><summary>Answer</summary>

**Answer: C** - Reading the key from the environment keeps it out of anything you might save, share, or commit.

</details>

### Q3. A response has `"finish_reason": "length"`. What does that mean?

- A. The model finished its answer normally
- B. The answer was cut off because it reached max_tokens
- C. The prompt was too long to read
- D. The model refused to answer

<details><summary>Answer</summary>

**Answer: B** - `length` means the token cap stopped it. `stop` means it ended on its own.

</details>

### Q4. You want the same request answered by a stronger model. What do you change?

- A. The URL of the gateway
- B. The `model` field in the request body
- C. The Authorization header
- D. The `role` of the user message

<details><summary>Answer</summary>

**Answer: B** - With a gateway, every model is behind the same URL and key. The `model` field picks which one answers.

</details>
