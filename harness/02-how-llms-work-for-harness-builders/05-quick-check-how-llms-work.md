---
type: quiz
title: "Quick check: how LLMs work"
minutes: 4
---

### Q1. Your agent read a file at step 2. At step 9 the model acts as if it never saw it. What's the most likely cause?

- A. The model's training data is out of date
- B. Temperature was set too low
- C. The file's tool result was dropped from the messages sent at step 9
- D. The model's memory was full

<details><summary>Answer</summary>

**Answer: C** - Models are stateless. If the step-2 result isn't in the step-9 request - dropped to save room, or never appended - the model can't see it.

</details>

### Q2. A model confidently states a config value that doesn't exist in any file. What is happening?

- A. The model is lying on purpose
- B. The gateway changed the answer
- C. The model is continuing text with the most plausible-looking tokens because the real value isn't in its context
- D. The model searched the internet and found a wrong value

<details><summary>Answer</summary>

**Answer: C** - Next-token prediction always produces fluent text. Without a source of truth in context, fluent means plausible, not correct.

</details>

### Q3. Which harness change best contains drift on a 40-step task?

- A. Remove the system prompt to save tokens
- B. Raise max_tokens
- C. Switch to streaming
- D. Repeat the goal and rules in the system prompt sent on every call, and cap the number of steps

<details><summary>Answer</summary>

**Answer: D** - Drift happens when the goal is buried under recent text. Resending it every call and limiting the steps keeps the model anchored.

</details>

### Q4. Why does a chat app appear to remember earlier messages?

- A. The app re-sends the conversation history with every request
- B. The model stores each conversation on the provider's servers
- C. The model fine-tunes itself after each message
- D. Tokens from earlier calls stay loaded in GPU memory

<details><summary>Answer</summary>

**Answer: A** - The app (a harness) keeps the messages list and sends it every time. The model itself starts fresh on each call.

</details>

### Q5. Setting max_tokens=1 and calling repeatedly, appending each reply, shows you...

- A. a bug in the API
- B. how embeddings work
- C. the generation loop a model runs internally: one token, append, repeat
- D. the model's training process

<details><summary>Answer</summary>

**Answer: C** - An answer is next-token prediction repeated until a stop token or a limit - exactly what you replayed by hand.

</details>
