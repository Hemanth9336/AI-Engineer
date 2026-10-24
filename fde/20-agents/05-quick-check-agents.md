---
type: quiz
title: "Quick check: agents"
minutes: 4
---

### Q1. What's the working definition of an agent used in this topic?

- A. Any chatbot
- B. A model in a loop choosing which tools to call until it decides it's done
- C. A fine-tuned model
- D. A model with a long system prompt

<details><summary>Answer</summary>

**Answer: B** - Loop + tool choice + model-decided stopping.

</details>

### Q2. The user says 'open a ticket for it'. How does the agent know what 'it' is?

- A. It guesses
- B. The ticket tool knows
- C. The earlier tool call and its result are still in the messages history
- D. It asks the API

<details><summary>Answer</summary>

**Answer: C** - History includes tool messages.

</details>

### Q3. Which tool needs the most safeguards?

- A. track_parcel
- B. search_articles
- C. get_weather
- D. issue_refund

<details><summary>Answer</summary>

**Answer: D** - Action tools that change systems or move money need limits, confirmation and audit.

</details>

### Q4. A workflow always runs the same three steps. What should you build?

- A. An autonomous agent
- B. A fine-tuned model
- C. A multi-agent system
- D. A chain

<details><summary>Answer</summary>

**Answer: D** - Known steps belong in code.

</details>
