---
type: scenario
title: "Scenario: the incident and the empty window"
minutes: 11
---

It's 4pm on a Thursday. Production checkout is failing, and you open Claude Code to help trace it. It tells you you've reached your usage limit until 6:40pm. You spent the morning on a large migration with three parallel subagents.

### Q1. Which meter did you hit?

- A. Your subscription's rolling usage window
- B. The API rate limit
- C. --max-budget-usd
- D. Fast mode

<details><summary>Answer</summary>

**Answer: A** - A reset time on a signed-in subscription session means the usage window.

</details>

### Q2. What gets you working again right now, without breaking policy?

- A. Create a second personal account
- B. Use usage credits if your plan has them enabled, or switch to the team's API key or cloud provider configured for this
- C. Wait until 6:40pm no matter what
- D. Turn on fast mode

<details><summary>Answer</summary>

**Answer: B** - Extra usage, or an organization-provided API path, is the sanctioned way past a window.

</details>

### Q3. Why did the morning use so much?

- A. The migration was large
- B. Your prompts were long
- C. Background titles
- D. Three parallel subagents each had their own context, so the morning billed several full contexts at once

<details><summary>Answer</summary>

**Answer: D** - Parallelism multiplies tokens; it trades usage for wall-clock time.

</details>

### Q4. What would you change for next time?

- A. Never use subagents
- B. Disable hooks
- C. Use opus for everything
- D. Run long bulk jobs like migrations on API billing or in CI with caps, and keep the interactive window for work that needs you

<details><summary>Answer</summary>

**Answer: D** - Match the meter to the job: unattended bulk work belongs on metered automation.

</details>
