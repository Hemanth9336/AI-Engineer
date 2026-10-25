---
type: scenario
title: "Scenario: the profile that is signed in to everything"
minutes: 9
---

A developer wants Claude to test their app's OAuth login against staging. Their everyday Chrome profile is signed in to the company admin console, production AWS, their bank, and personal email. They plan to run `claude --chrome` in auto mode "so it doesn't keep asking".

### Q1. What's the core risk?

- A. Claude acts with every login in that profile; a confused step or a prompt injection on a page could touch production or personal accounts
- B. Slowness
- C. Screenshots are large
- D. OAuth won't work

<details><summary>Answer</summary>

**Answer: A** - Claude shares the browser's login state; the profile defines the blast radius.

</details>

### Q2. Which setup fits the task?

- A. The everyday profile
- B. Incognito with auto mode
- C. A separate browser profile signed in only to staging test accounts, with site permissions limited to staging
- D. Their colleague's laptop

<details><summary>Answer</summary>

**Answer: C** - Scope the logins to what the task needs.

</details>

### Q3. Is auto mode a good idea here?

- A. Yes, always
- B. Use Manual (or allow only the staging site) - prompts on unfamiliar sites are the safety net
- C. Only bypass works with Chrome
- D. It doesn't matter

<details><summary>Answer</summary>

**Answer: B** - Keep a human in the loop where actions can have real side effects.

</details>

### Q4. They need to upload a test certificate (`client.pem`) to the staging form. What happens?

- A. Claude Code refuses credential-named files like .pem; use a dedicated test fixture with a neutral name, or upload it yourself
- B. It uploads
- C. It uploads if under 10 MB
- D. Only in plan mode

<details><summary>Answer</summary>

**Answer: A** - Upload rules protect keys and secrets by name.

</details>
