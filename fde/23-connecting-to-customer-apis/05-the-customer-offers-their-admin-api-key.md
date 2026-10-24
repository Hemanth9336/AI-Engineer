---
type: scenario
title: "The customer offers their admin API key"
minutes: 3
---

Week one at Kestrel Bank. To save time, the platform lead sends you a message: "Here's the admin API key for our core banking sandbox and production - it can do everything, so you won't get blocked. Just paste it in the config."

### Q1. What do you do?

- A. Use it - it saves weeks
- B. Thank them, don't use it, and ask for a service account scoped to exactly what the assistant needs (read-only account balances in the sandbox first)
- C. Use it only in production
- D. Share it with the team so everyone can test

<details><summary>Answer</summary>

**Answer: B** - Least privilege - and the key was already exposed in a message.

</details>

### Q2. Why is an admin key in an AI assistant especially risky?

- A. Admin keys are slower
- B. If the assistant is tricked or confused into calling the wrong endpoint, nothing stops a destructive action
- C. Models can't use admin keys
- D. It costs more

<details><summary>Answer</summary>

**Answer: B** - The credential sets the blast radius of every mistake.

</details>

### Q3. The key was sent in a chat message. What else should happen?

- A. Nothing
- B. Delete the message and forget it
- C. Recommend rotating it, since it's been shared outside a secrets manager
- D. Post it in the runbook

<details><summary>Answer</summary>

**Answer: C** - Treat a shared secret as compromised.

</details>
