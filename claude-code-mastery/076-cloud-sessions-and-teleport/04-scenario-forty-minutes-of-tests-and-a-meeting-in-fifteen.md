---
type: scenario
title: "Scenario: forty minutes of tests and a meeting in fifteen"
minutes: 9
---

You're midway through fixing a flaky integration suite. A full run takes 40 minutes, and you have a meeting in 15. Your branch has two local commits you haven't pushed, plus an uncommitted change to a test helper.

### Q1. You run `claude --cloud "keep fixing the flaky suite"` right away. What will the cloud session see?

- A. Everything on your laptop
- B. Only what's on GitHub for this branch - not your two local commits or the uncommitted change
- C. Nothing
- D. Only the uncommitted change

<details><summary>Answer</summary>

**Answer: B** - The VM clones the remote; push first.

</details>

### Q2. What do you do in the two minutes before leaving?

- A. Nothing
- B. Commit the helper change, push the branch, then start claude --cloud with a specific task and a stop condition
- C. Email yourself the diff
- D. Start Remote Control

<details><summary>Answer</summary>

**Answer: B** - Push makes the work visible to the VM; a clear task makes the run useful.

</details>

### Q3. The suite needs a database container. Where do you set that up?

- A. In the prompt
- B. In the cloud environment's setup script (cached), with any credentials as network secrets
- C. In CLAUDE.md
- D. In .env committed to the repo

<details><summary>Answer</summary>

**Answer: B** - Setup scripts prepare the VM; secrets never go in environment variables or the repo.

</details>

### Q4. After the meeting, how do you continue at your desk?

- A. Start over locally
- B. claude --resume
- C. claude --teleport <id>: it checks out the session's branch and loads the conversation
- D. git pull only

<details><summary>Answer</summary>

**Answer: C** - Teleport brings both the branch and the conversation.

</details>
