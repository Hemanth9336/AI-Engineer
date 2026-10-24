---
type: scenario
title: "The pilot worked, the customer wants to skip hardening"
minutes: 5
---

Your support-assistant pilot hit its target: 88% correct on the test set and agents love it. The sponsor says: "This is great - just turn it on for all 400 agents tomorrow. We'll worry about the security review and cost limits later."

### Q1. What is the right response?

- A. Turn it on - the customer is in charge
- B. Turn it on but secretly add limits later
- C. Refuse to continue the engagement
- D. Explain what production adds (cost limits, logging, guardrails, security approval), estimate how long it takes, and offer a staged rollout while it's done

<details><summary>Answer</summary>

**Answer: D** - Production work protects the customer. Make the risk concrete and offer a path that keeps momentum.

</details>

### Q2. Which risk is most concrete to raise with the sponsor?

- A. The pilot users might leave
- B. The model might get bored
- C. Going from 10 to 400 agents multiplies cost and blast radius, with no spending limit and no logs to investigate a bad answer
- D. The test set is too small to matter

<details><summary>Answer</summary>

**Answer: C** - Costs and incidents scale with users; without limits and logs you can't control or debug either.

</details>

### Q3. What could you safely do quickly while hardening continues?

- A. Nothing
- B. Expand to a second team of 30 agents with a daily spend cap and logging switched on
- C. Remove the refusal rules to make it more helpful
- D. Give every agent admin access

<details><summary>Answer</summary>

**Answer: B** - A staged rollout with basic limits keeps value flowing without taking on the full risk.

</details>
