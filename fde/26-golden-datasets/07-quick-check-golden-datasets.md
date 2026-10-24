---
type: quiz
title: "Quick check: golden datasets"
minutes: 3
---

### Q1. What should an expected answer contain?

- A. The exact wording the bot must use
- B. A score from 1 to 10
- C. A link to the docs
- D. The checkable facts a correct answer must include

<details><summary>Answer</summary>

**Answer: D** - Facts, not phrasing.

</details>

### Q2. Where do the most realistic eval questions come from?

- A. Brainstorming
- B. The model itself
- C. Real support tickets, chat logs and search logs
- D. Article titles

<details><summary>Answer</summary>

**Answer: C** - Real users phrase things you won't think of.

</details>

### Q3. Why de-duplicate mined questions but keep the counts?

- A. To save disk
- B. Counts are required by JSONL
- C. One case per distinct question keeps the set clean; the count shows how much each matters
- D. To hide volume

<details><summary>Answer</summary>

**Answer: C** - Unique cases, weighted by demand.

</details>

### Q4. Which is the best trap question for Meridian's bot?

- A. How much does DDP cost?
- B. Who won the World Cup?
- C. When is support open?
- D. Write a poem

<details><summary>Answer</summary>

**Answer: A** - On-topic, near a real document, and not answered by it.

</details>

### Q5. Why report scores per slice?

- A. It looks better
- B. Slices are cheaper
- C. A blended score can hide failures on hard or trap questions
- D. Customers prefer more numbers

<details><summary>Answer</summary>

**Answer: C** - Per-slice scores show where it breaks.

</details>
