---
type: quiz
title: "Quick check: asking for help"
minutes: 4
---

### Q1. When should an agent ask the user instead of using a tool?

- A. Whenever it's unsure about anything
- B. Never - agents should be autonomous
- C. Before every tool call
- D. When the missing piece is something only the user knows, like a preference or a choice between valid targets

<details><summary>Answer</summary>

**Answer: D** - Look up what can be looked up; ask about what only the user can decide.

</details>

### Q2. How does the model ask a question in a harness with an ask_user tool?

- A. It calls ask_user; the harness shows the question and returns the answer as the tool result
- B. It writes the question in its final answer
- C. The provider pauses the request
- D. It sets temperature to 0

<details><summary>Answer</summary>

**Answer: A** - Asking is a tool call like any other - the harness decides how to reach the user.

</details>

### Q3. Your agent runs in a nightly job with no user. What should ask_user return?

- A. An empty string
- B. A random choice
- C. A clear error such as 'the user is not available - stop and explain what you need'
- D. It should block until morning

<details><summary>Answer</summary>

**Answer: C** - The model can then end with a useful request for input instead of hanging or guessing.

</details>

### Q4. The agent asks 'Which folder are the configs in?' What does that suggest?

- A. Good caution
- B. list_dir is broken
- C. The model needs a bigger context window
- D. The ask_user description doesn't say to look things up with the other tools first

<details><summary>Answer</summary>

**Answer: D** - The answer was discoverable. Steer the model with the description: don't ask about what tools can find.

</details>
