---
type: quiz
title: "Quick check: the system prompt"
minutes: 4
---

### Q1. What belongs in a harness system prompt?

- A. The role, when to use each tool, rules with reasons, what to do when stuck, and the answer format
- B. The API key so the model can call services
- C. The full help center
- D. This user's account details

<details><summary>Answer</summary>

**Answer: A** - Keys never go near the model, documents come from retrieval, and per-user data comes from tools or the conversation.

</details>

### Q2. Why keep the system prompt in its own file?

- A. Models read files faster
- B. Files use fewer tokens
- C. It can be reviewed, versioned and tested like code - and changed without touching the loop
- D. The API requires it

<details><summary>Answer</summary>

**Answer: C** - Prompt changes change behavior. Treat them like code changes.

</details>

### Q3. A prompt says 'Always answer immediately' and later 'Always look up the account first'. What happens?

- A. The model follows the last one
- B. Behavior becomes unreliable - fix the contradiction
- C. The model follows the first one
- D. The API rejects the prompt

<details><summary>Answer</summary>

**Answer: B** - Contradictory rules make the model choose differently from run to run.

</details>

### Q4. Which rule is most likely to be followed?

- A. NEVER EVER PROMISE REFUNDS!!!
- B. Don't do refunds.
- C. Never promise a refund; refunds are decided by the billing team, so open a ticket instead.
- D. Maybe avoid refunds.

<details><summary>Answer</summary>

**Answer: C** - Specific, calm, with a reason and the alternative action.

</details>

### Q5. Privacy must never be violated. What should you do besides writing the rule?

- A. Enforce it in the harness, for example by only returning data for the customer's own email
- B. Repeat it five times
- C. Make it bold
- D. Trust the model

<details><summary>Answer</summary>

**Answer: A** - Prompts make good behavior likely; harness controls make bad behavior impossible.

</details>
