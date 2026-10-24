---
type: scenario
title: "Scenario: choosing a model for a batch job"
minutes: 4
---

Every night a job sends about 200,000 short support tickets to a model, which labels each one as `billing`, `bug`, `outage`, or `question`. It runs on `lab-smart` today and costs more than the rest of the team's cloud bill. On a 200-ticket test set, `lab-smart` labels 97% correctly, `lab-fast` 96%, and `lab-mini` 94%.

### Q1. Which model is the sensible default for this job?

- A. lab-smart - it has the best accuracy
- B. lab-fast or lab-mini - nearly the same accuracy at a fraction of the cost
- C. lab-reasoning - labelling needs deep thought
- D. Whichever is newest

<details><summary>Answer</summary>

**Answer: B** - A 1-3 point accuracy gap rarely justifies many times the cost for simple classification.

</details>

### Q2. The team worries about the tickets the cheaper model gets wrong. What is a good design?

- A. Use the cheap model, and send only low-confidence or 'outage' tickets to a stronger model or a person
- B. Run everything on lab-smart forever
- C. Ignore the errors
- D. Run each ticket on all five models

<details><summary>Answer</summary>

**Answer: A** - Routing the hard minority to a stronger model keeps most of the savings.

</details>

### Q3. Six months later the provider releases new models. What should you do?

- A. Nothing - the test set is no longer useful
- B. Re-run the same test set on the candidates and switch the alias if a cheaper one passes
- C. Always switch to the newest model immediately
- D. Rewrite the whole job

<details><summary>Answer</summary>

**Answer: B** - Keep the test set; it makes re-evaluating a quick, measured decision.

</details>
