---
type: quiz
title: "Quick check: conversation state"
minutes: 3
---

### Q1. Why doesn't the model remember a previous API request?

- A. It's a bug
- B. The key changed
- C. The temperature was 0
- D. Every request is independent - it only sees the messages you send

<details><summary>Answer</summary>

**Answer: D** - State lives in your application.

</details>

### Q2. Your chat loop only appends user messages. What goes wrong?

- A. Nothing
- B. It gets cheaper
- C. The model sees questions without its earlier answers and loses track
- D. The system prompt disappears

<details><summary>Answer</summary>

**Answer: C** - Append the assistant replies too.

</details>

### Q3. Why does a 30-turn conversation cost more per request than a 3-turn one?

- A. Models charge more for long chats
- B. The model thinks harder
- C. Each request re-sends all previous turns
- D. It doesn't

<details><summary>Answer</summary>

**Answer: C** - Input tokens grow with the history.

</details>

### Q4. When you trim history a second time, what should the summarizer receive?

- A. Only the newly dropped messages
- B. Nothing
- C. The previous summary plus the newly dropped messages
- D. The whole conversation

<details><summary>Answer</summary>

**Answer: C** - Otherwise the new summary forgets what the old one held.

</details>
