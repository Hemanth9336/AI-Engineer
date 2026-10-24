---
type: scenario
title: "The provider deprecates your pilot's model"
minutes: 3
---

Week five of Meridian's pilot. The provider emails: the model behind `lab-fast` will be retired in 60 days, and recommends a newer one. The newer model is cheaper and scores higher on public benchmarks. The pilot review is in three weeks.

### Q1. What do you do first?

- A. Switch everything to the new model today - it's better
- B. Ignore it until day 59
- C. Run your eval suite on the new model with the current prompt and compare the scores
- D. Ask the customer to choose

<details><summary>Answer</summary>

**Answer: C** - Measure on your own tests before changing anything.

</details>

### Q2. The new model scores higher overall but now ignores the exact refusal sentence 20% of the time. What next?

- A. Ship it - overall is higher
- B. Stay on the old model forever
- C. Create a new prompt version that fixes the refusal behaviour, re-run the evals, then plan a staged switch
- D. Remove refusals from the eval suite

<details><summary>Answer</summary>

**Answer: C** - A new prompt version plus re-measurement - and the switch remains reversible.

</details>

### Q3. How should the switch reach production?

- A. Change the model name in the code and deploy
- B. Run both models and average the answers
- C. Change the gateway alias for a share of traffic, compare metrics, then move the rest - with a rollback switch
- D. Ask users which they prefer

<details><summary>Answer</summary>

**Answer: C** - Staged, config-only, reversible.

</details>
