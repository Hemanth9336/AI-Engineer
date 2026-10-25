---
type: quiz
title: "Quick check: exact answers from data"
minutes: 11
---

### Q1. You paste a 240-row CSV into the prompt and ask for the total. The answer looks plausible. How far can you trust it?

- A. Fully, models are good at sums
- B. Not at all until code computes it - mental arithmetic over many rows is unreliable
- C. It is right within 1%
- D. Only if you ask twice

<details><summary>Answer</summary>

**Answer: B** - Have the agent write and run the arithmetic.

</details>

### Q2. Two analysts get different 'Q3 revenue' numbers from the same file. The most likely reason?

- A. One used a different model
- B. Different definitions: returns, date bounds, gross or net
- C. Floating point
- D. The CSV changed

<details><summary>Answer</summary>

**Answer: B** - Pin definitions in the question.

</details>

### Q3. Why keep analysis.py after you have the answers?

- A. To save tokens
- B. Claude needs it
- C. It is the audit trail: anyone can re-run it and get the same numbers
- D. Git requires it

<details><summary>Answer</summary>

**Answer: C** - A number without its code is an opinion.

</details>

### Q4. Which sanity check catches a filter bug in a per-region breakdown?

- A. Counting the questions
- B. Checking that per-region totals sum to the overall total
- C. Re-reading the prompt
- D. Sorting the output

<details><summary>Answer</summary>

**Answer: B** - Reconciliation exposes dropped or double-counted rows.

</details>
