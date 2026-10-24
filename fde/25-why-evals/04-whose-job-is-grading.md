---
type: scenario
title: "Whose job is grading"
minutes: 4
---

Kestrel Bank's pilot needs its first eval run: 100 questions about lending policy. Your team can write a model judge in an afternoon. The bank's policy team says they're busy and asks you to "just handle the grading".

### Q1. Why shouldn't you grade everything alone?

- A. It takes too long
- B. You aren't the policy expert - you can't reliably tell a subtly wrong lending rule from a right one, and the bank won't trust a score only you produced
- C. Judges are illegal in banking
- D. Graders must be lawyers

<details><summary>Answer</summary>

**Answer: B** - Domain experts define correctness; the customer must trust the score.

</details>

### Q2. What's a practical split of the work?

- A. The bank grades all 100 answers every release
- B. Only automated keyword checks
- C. Only the model judge, forever
- D. Experts write the expected answers and grade an initial sample; a model judge grades every run; experts spot-check the judge's verdicts regularly

<details><summary>Answer</summary>

**Answer: D** - Experts set the standard once; automation applies it every run; spot-checks keep it honest.

</details>

### Q3. The judge and the experts disagree on 12 of 50 sampled answers. What now?

- A. Trust the judge
- B. Read the disagreements, fix the rubric or the expected answers, and re-measure agreement before relying on the judge
- C. Trust the experts and drop the judge
- D. Average the two

<details><summary>Answer</summary>

**Answer: B** - Judge agreement with experts is itself something you measure and improve (topic 27).

</details>
