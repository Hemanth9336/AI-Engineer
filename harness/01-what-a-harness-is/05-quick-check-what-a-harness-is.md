---
type: quiz
title: "Quick check: what a harness is"
minutes: 5
---

### Q1. Which of these is part of the harness rather than the model?

- A. The probabilities the model assigns to the next token
- B. The code that decides whether a requested shell command may run
- C. The knowledge the model picked up during training
- D. The writing style the model tends to use

<details><summary>Answer</summary>

**Answer: B** - The permission check is ordinary code you write around the model. Token probabilities, training knowledge and style all live inside the model.

</details>

### Q2. A support bot forgets what the customer said three messages ago. Which harness part is responsible?

- A. Permissions
- B. Evals
- C. Context management
- D. Tools

<details><summary>Answer</summary>

**Answer: C** - What the model sees on each call is decided by context management. If earlier messages aren't sent, or were dropped to save room, the model simply can't see them.

</details>

### Q3. A team keeps adding 'NEVER guess' to its prompt, but the bot still invents answers about files it can't see. What's the real fix?

- A. Give the bot a tool that reads the file
- B. Write NEVER in capital letters and repeat it three times
- C. Raise the temperature so it explores more answers
- D. Use a shorter system prompt

<details><summary>Answer</summary>

**Answer: A** - Apply the careful-human test: nobody can answer about a file they can't see. Change what the model can see and do - give it a tool.

</details>

### Q4. In Claude Code, who decides whether a risky command is allowed to run?

- A. The model, based on its system prompt
- B. Nobody - Claude Code runs whatever the model asks for
- C. The harness, using rules the model cannot change
- D. The provider's servers

<details><summary>Answer</summary>

**Answer: C** - The model only asks. The harness checks the request against its permission rules and, for risky commands, asks you first.

</details>

### Q5. Why do evals belong in the harness?

- A. They make each model call faster
- B. They prove a change to the prompt, tools or loop made the agent better, not worse
- C. They replace the need for permissions
- D. They reduce the number of tokens per request

<details><summary>Answer</summary>

**Answer: B** - Without evals, 'version 14 is better than version 13' is a guess. Evals turn it into a measured fact.

</details>
