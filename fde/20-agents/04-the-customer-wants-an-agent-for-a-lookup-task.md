---
type: scenario
title: "The customer wants an agent for a lookup task"
minutes: 4
---

Meridian's head of customer service has read about AI agents. She wants "an autonomous agent with access to all our systems" for one job: telling customers where their order is. 95% of these questions include an order id; the answer is the status and ETA from one API.

### Q1. What do you recommend?

- A. An autonomous agent with every system's API as a tool
- B. No AI at all
- C. A simple chain: extract the order id, call the tracking API, write the answer - with one fallback question when the id is missing
- D. A fine-tuned model

<details><summary>Answer</summary>

**Answer: C** - The steps are known; a chain is cheaper, faster and easier to test.

</details>

### Q2. She asks why not give it all the tools 'just in case'. What's the strongest reason?

- A. Tools are expensive to define
- B. Models can only use one tool
- C. More tools and autonomy mean more ways to fail - wrong tool, extra actions, unpredictable cost - and more access to protect, with no benefit for this task
- D. It's against the API terms

<details><summary>Answer</summary>

**Answer: C** - Every tool is attack surface and failure surface.

</details>

### Q3. When would you revisit an agent?

- A. Never
- B. When the questions grow into open-ended investigations whose steps depend on what each lookup finds
- C. When the model gets bigger
- D. When the customer asks again

<details><summary>Answer</summary>

**Answer: B** - Agents earn their place when the path can't be known in advance.

</details>
