---
type: scenario
title: "Scenario: the key in the script"
minutes: 4
---

A teammate shares a handy script in the team repo. Near the top it says `client = OpenAI(api_key="sk-proj-4fJ...")`. The repo is private, the script works, and they say "it's fine, only we can see it".

### Q1. What is the real risk?

- A. The key is now in git history, every clone, CI logs, and any fork - anyone who ever reads it can spend on that account
- B. None - the repo is private
- C. The script will run slower
- D. OpenAI will reject hard-coded keys

<details><summary>Answer</summary>

**Answer: A** - Secrets in git spread to every copy and live forever in history.

</details>

### Q2. What should happen first?

- A. Revoke (rotate) the key at the provider, then remove it from the code
- B. Delete the line and commit
- C. Make the repo more private
- D. Rename the variable

<details><summary>Answer</summary>

**Answer: A** - Deleting the line doesn't un-leak it. Revoke the key first; history still has the old one.

</details>

### Q3. How should the script get the key instead?

- A. From a comment in the code
- B. From a file committed next to the script
- C. From the environment, e.g. OpenAI() reading OPENAI_API_KEY, set from a secret store
- D. Ask the model for it

<details><summary>Answer</summary>

**Answer: C** - Keep secrets in the environment or a secret manager; SDKs read them automatically.

</details>
