---
type: quiz
title: "Quick check: tools are prompts"
minutes: 4
---

### Q1. The model never calls your search_logs tool, even for 'any errors in billing?'. What's the first thing to change?

- A. Switch models
- B. Add more tools
- C. Rename the parameters to single letters
- D. The description: say what it searches and that it's for questions about errors, timeouts and crashes

<details><summary>Answer</summary>

**Answer: D** - The 'when to use it' sentence is what makes a model reach for a tool.

</details>

### Q2. Which parameter design best prevents the model from sending 'Search Service' or 'srch'?

- A. "service": {"type": "string"}
- B. "service": {"type": "string", "enum": ["billing", "search"]}
- C. A note in the system prompt
- D. Accepting anything and guessing in code

<details><summary>Answer</summary>

**Answer: B** - An enum turns a free-text guess into a fixed choice the model can see.

</details>

### Q3. Which error message helps the model fix its next call in one step?

- A. error
- B. error: unknown metric 'latency'. Valid metrics: error_rate, p95_ms, restarts
- C. error: invalid input
- D. 500

<details><summary>Answer</summary>

**Answer: B** - It names the bad value and lists the valid ones - the model can correct itself immediately.

</details>

### Q4. How should you decide whether a new tool description is better?

- A. Read it carefully
- B. Run the same questions against old and new versions and compare how often - and how well - the tool gets called
- C. Count the words
- D. Ask the model which one it prefers

<details><summary>Answer</summary>

**Answer: B** - Descriptions are prompts; their effect is measured, not read.

</details>

### Q5. A tool named `get` with params `q` and `t` mixes logs, metrics and restarts. What's the main redesign principle?

- A. One job per tool, a specific verb+noun name, and typed, described parameters
- B. Shorter names
- C. Make every parameter optional
- D. Put all the documentation in the system prompt instead

<details><summary>Answer</summary>

**Answer: A** - Specific, single-purpose tools with explicit parameters leave little room for misuse.

</details>
