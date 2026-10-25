---
type: scenario
title: "Scenario: the request to log prompts"
minutes: 8
---

A product manager asks you to set `OTEL_LOG_USER_PROMPTS=1` org-wide "so we can see what people use Claude Code for". Telemetry goes to the company's shared observability platform, which 300 engineers can query and which keeps data for 13 months.

### Q1. What's the main risk?

- A. Higher telemetry cost
- B. Slower sessions
- C. Prompts contain pasted code, secrets, and customer data, which would land in a widely readable store for 13 months
- D. Nothing - it's internal

<details><summary>Answer</summary>

**Answer: C** - The backend's access and retention, not Claude Code's, become the controls on that data.

</details>

### Q2. Which signals answer "what do people use it for" without prompt text?

- A. Tool usage from tool_result events, sessions, active time, lines changed, and model and cost metrics, sliced by team via resource attributes
- B. None
- C. Only cost
- D. The prompt length

<details><summary>Answer</summary>

**Answer: A** - Behaviour is visible from metadata; content isn't needed.

</details>

### Q3. If a narrow study truly needs prompt text, what makes it acceptable?

- A. A Slack announcement
- B. Turning it on for a week org-wide
- C. Opt-in for a named group, a separate restricted backend with short retention, and a written purpose
- D. Hashing the prompts

<details><summary>Answer</summary>

**Answer: C** - Limit scope, access, and retention to match the sensitivity.

</details>

### Q4. How do you keep individual users from turning on content logging themselves?

- A. Ask nicely
- B. Remove the env var from docs
- C. Set the OTEL env in managed settings, which users can't override
- D. Use a proxy

<details><summary>Answer</summary>

**Answer: C** - Managed settings take precedence over user and project settings (topic 070).

</details>
