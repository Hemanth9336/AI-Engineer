---
type: quiz
title: "Quick check: LangChain"
minutes: 6
---

### Q1. What does StrOutputParser do at the end of a chain?

- A. Calls the model
- B. Turns the model's message object into a plain string
- C. Fills in the template
- D. Counts tokens

<details><summary>Answer</summary>

**Answer: B** - The model returns an AIMessage; the parser extracts the text.

</details>

### Q2. When is the plain SDK a better choice than LangChain?

- A. Never
- B. When you build agents with tools
- C. When you need many providers
- D. For a single, simple API call where extra layers only make debugging harder

<details><summary>Answer</summary>

**Answer: D** - Frameworks pay off when you use several of their pieces.

</details>

### Q3. Your template includes a JSON example like {"level": "high"} and LangChain complains about a missing variable. Why?

- A. Braces mark placeholders - literal braces must be doubled as {{ and }}
- B. JSON isn't allowed
- C. The model is wrong
- D. You need a JSON parser

<details><summary>Answer</summary>

**Answer: A** - Single braces are template variables.

</details>

### Q4. How do you see exactly what messages a chain sends?

- A. You can't
- B. Invoke the prompt template alone and print its messages, or check the gateway log
- C. Increase temperature
- D. Read the LangChain source

<details><summary>Answer</summary>

**Answer: B** - Run each step alone to debug.

</details>
