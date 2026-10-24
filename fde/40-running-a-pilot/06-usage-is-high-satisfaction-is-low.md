---
type: scenario
title: "Usage is high, satisfaction is low"
minutes: 3
---

Week 3 of the Harbor Foods pilot: all 6 agents use the drafts on most tickets (adoption target met), but 41% of drafts get a thumbs-down and agents rewrite most of them. Golden-set correctness is still 89%.

### Q1. What's the most likely explanation for high golden-set scores but low satisfaction?

- A. Agents dislike AI
- B. The golden set doesn't match the real traffic - agents are getting questions or formats the eval doesn't cover
- C. The thumbs-down button is broken
- D. The model is too big

<details><summary>Answer</summary>

**Answer: B** - When evals and users disagree, the eval set is usually missing something.

</details>

### Q2. What do you do this week?

- A. Wait for week 6
- B. Switch to a bigger model
- C. Read every thumbs-down and comment, bucket them, add representative cases to the golden set, and fix the top bucket
- D. Remove the thumbs-down button

<details><summary>Answer</summary>

**Answer: C** - Feedback becomes eval cases becomes fixes.

</details>

### Q3. Reading the comments, most say 'answer is right but too long, I delete half'. What now?

- A. Ignore it - correctness is fine
- B. Disable drafts
- C. Train the agents to accept long drafts
- D. Treat it as a real quality issue: adjust the prompt for shorter drafts, add a length check to the evals, and measure the edit rate next week

<details><summary>Answer</summary>

**Answer: D** - Users define quality too - make it measurable.

</details>
