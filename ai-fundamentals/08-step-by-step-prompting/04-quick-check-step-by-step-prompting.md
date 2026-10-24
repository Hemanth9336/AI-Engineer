---
type: quiz
title: "Quick check: step-by-step prompting"
minutes: 6
---

### Q1. Why does asking a model to work step by step improve accuracy on multi-step problems?

- A. Each intermediate result is written down, so later steps build on it instead of jumping to an answer
- B. It makes the model run on faster hardware
- C. It switches the model to a calculator
- D. It removes the randomness from the answer

<details><summary>Answer</summary>

**Answer: A** - The written steps act as scratch paper the model can build on, token by token.

</details>

### Q2. A script needs only the final number from a step-by-step answer. What prompt design helps most?

- A. Ask for the answer in bold
- B. Ask for the answer first, then no steps
- C. Ask it to be confident
- D. Ask it to end with a line in a fixed form such as ANSWER: <number>

<details><summary>Answer</summary>

**Answer: D** - A fixed, marked final line is trivial for a script to extract.

</details>

### Q3. Which task benefits least from step-by-step prompting?

- A. Translating 'good morning' into French
- B. Diagnosing why a deploy fails only on Fridays
- C. Estimating monthly cloud cost from usage numbers
- D. Comparing three database options against four requirements

<details><summary>Answer</summary>

**Answer: A** - A short translation has no chain of steps; asking for reasoning just adds tokens.

</details>

### Q4. The model's steps look convincing and end with the right answer. What is still wise for a budget decision?

- A. Nothing - convincing steps are proof
- B. Check the steps and redo the arithmetic yourself or in code
- C. Ask the same model if it is sure
- D. Run it with max_tokens lower

<details><summary>Answer</summary>

**Answer: B** - Steps can contain errors. Visible reasoning is valuable because you can verify it.

</details>
