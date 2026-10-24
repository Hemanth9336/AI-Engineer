---
type: quiz
title: "Quick check: prompting basics"
minutes: 4
---

### Q1. Which prompt is most likely to get a usable answer first time?

- A. Explain what a Docker image is to a support agent who has never used a terminal, in 3 sentences, with one everyday analogy.
- B. Explain Docker in detail, be thorough and comprehensive.
- C. Tell me about Docker.
- D. Docker?

<details><summary>Answer</summary>

**Answer: A** - It names the task, the audience, the length, and a format detail. Asking to be 'thorough' adds length, not clarity.

</details>

### Q2. Where does 'Always answer in under 100 words and never give legal advice' belong?

- A. In the system message
- B. In every user message
- C. In the assistant message
- D. In max_tokens

<details><summary>Answer</summary>

**Answer: A** - Rules that apply to every request belong in the system message. The user message carries the specific task.

</details>

### Q3. Your prompt says 'Don't be too long.' What is the better rewrite?

- A. Don't be long at all.
- B. Please be short.
- C. Be concise, brief, and short.
- D. Answer in at most two sentences.

<details><summary>Answer</summary>

**Answer: D** - A specific, positive target is easier to follow than a vague 'don't'.

</details>

### Q4. Why does adding a reason, like 'these bullets are read on a phone during an outage', help?

- A. It makes the prompt longer, which always helps
- B. It lets the model make sensible choices you didn't spell out, like short words and no tables
- C. Models ignore everything except the reason
- D. It lowers the token cost

<details><summary>Answer</summary>

**Answer: B** - A reason tells the model what you are optimizing for, so its unwritten choices go your way.

</details>
