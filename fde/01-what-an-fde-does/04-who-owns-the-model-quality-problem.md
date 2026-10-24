---
type: quiz
title: "Who owns the model quality problem"
minutes: 4
---

### Q1. Week two at the bank. Your document assistant gives weak answers to questions about mortgage rules. You check: retrieval finds the right policy pages, but the model misreads a table that lists rates by loan size. Whose problem is it right now?

- A. The ML engineer's - the model is weak, so wait for a better one
- B. Yours - the customer needs a working solution, so you work around it: reformat the table, adjust the prompt, or route these questions differently, and measure the result
- C. The solutions architect's - the plan was wrong
- D. The bank's - their table format is unusual

<details><summary>Answer</summary>

**Answer: B** - The FDE is measured on whether the customer has a working solution. Model limits are a constraint you design around, not a reason to wait.

</details>

### Q2. Your workaround helps, but one failure pattern remains: the model consistently misreads a specific kind of financial table, at every customer you have seen. What else do you do?

- A. Nothing - it works well enough here
- B. Write up the failing cases with examples and send them to the vendor's ML engineers, because a fix in the model helps every customer
- C. Tell the bank the model is broken
- D. Fine-tune a new model yourself over the weekend

<details><summary>Answer</summary>

**Answer: B** - FDEs are the vendor's eyes in the field. Well-documented failure cases are exactly what the ML team needs - and the fix reaches every customer at once.

</details>

### Q3. Which statement best describes the split of responsibility?

- A. The FDE owns the outcome at this customer; the ML engineer owns the model's general capability
- B. The ML engineer owns everything about quality
- C. The architect owns quality because they chose the design
- D. Nobody owns quality until production

<details><summary>Answer</summary>

**Answer: A** - Outcome at the customer: FDE. The model's capability across all customers: ML engineering.

</details>
