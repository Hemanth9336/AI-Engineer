---
type: scenario
title: "Scenario: picking the next fix"
minutes: 4
---

You are refining a prompt that summarizes support tickets for a weekly report. You have run it on five real tickets. The summaries are accurate, but two of them are four paragraphs long, one starts with "Certainly! Here is a summary:", and one says the customer is "on the Enterprise plan" when the ticket never mentions a plan.

### Q1. Which single change should you make first for the long summaries?

- A. Switch to the strongest model
- B. Raise the temperature
- C. Add a precise length limit, such as 'at most 2 sentences'
- D. Add more tickets to the prompt

<details><summary>Answer</summary>

**Answer: C** - Length is unspecified, so the model guessed. A numeric limit is the direct fix.

</details>

### Q2. What fixes the 'on the Enterprise plan' detail?

- A. Tell the model to use only facts stated in the ticket, and to omit anything not mentioned
- B. Nothing; it is probably true
- C. Remove the system message
- D. Ask it to be more creative

<details><summary>Answer</summary>

**Answer: A** - It invented a plausible fact. Restrict it to the ticket and allow it to leave things out.

</details>

### Q3. You add a length limit, a no-introduction rule, and a facts-only rule all at once, and three summaries get better while one gets worse. What did you lose?

- A. Nothing, it is better overall
- B. The ability to tell which change helped and which one hurt
- C. Your token budget
- D. The temperature setting

<details><summary>Answer</summary>

**Answer: B** - Change one thing at a time so each result tells you something.

</details>
