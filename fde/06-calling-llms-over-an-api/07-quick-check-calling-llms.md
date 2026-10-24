---
type: quiz
title: "Quick check: calling LLMs"
minutes: 3
---

### Q1. Where is the reply text in a chat completion response?

- A. choices[0].message.content
- B. usage.content
- C. messages[0].content
- D. reply.text

<details><summary>Answer</summary>

**Answer: A** - The first choice's message content.

</details>

### Q2. A reply ends mid-sentence and finish_reason is "length". Why?

- A. The model crashed
- B. It hit max_tokens
- C. The temperature was 0
- D. The system message was too long

<details><summary>Answer</summary>

**Answer: B** - length means the output cap was reached.

</details>

### Q3. Where should a support bot's company policies go?

- A. In the system message
- B. In the user message, pasted by the user
- C. In max_tokens
- D. Nowhere - the model knows them

<details><summary>Answer</summary>

**Answer: A** - Developer-supplied facts and rules belong in the system message.

</details>

### Q4. Why does `OpenAI()` take no key in the code?

- A. It reads OPENAI_API_KEY and OPENAI_BASE_URL from the environment
- B. It doesn't need one
- C. The key is built in
- D. It asks the user

<details><summary>Answer</summary>

**Answer: A** - Environment configuration keeps keys out of code and lets the same script run anywhere.

</details>
