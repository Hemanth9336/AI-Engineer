---
type: scenario
title: "Scenario: the phone that drove your workstation"
minutes: 9
---

You left `claude remote-control` running on your workstation over the weekend, started with `--permission-mode bypassPermissions` "so the phone wouldn't keep asking". On Monday the shell history shows commands you didn't run. Your claude.ai password had been reused on another site.

### Q1. How did someone run commands on your workstation?

- A. A bug in Remote Control
- B. Your claude.ai account was the door: anyone signed in to it can drive your published sessions, and bypass mode removed every prompt
- C. An open inbound port
- D. The Anthropic API was compromised

<details><summary>Answer</summary>

**Answer: B** - Remote Control only makes outbound connections; the account and the session's permission mode are the boundary.

</details>

### Q2. Which two changes matter most?

- A. Use a different terminal
- B. Rename the sessions
- C. Lower --capacity
- D. Secure the account (unique password, MFA, Trusted Devices) and never publish a bypass-mode session

<details><summary>Answer</summary>

**Answer: D** - Protect who can drive, and keep prompts on for remote control.

</details>

### Q3. What else should you do now?

- A. Treat it as an incident: rotate credentials reachable from that machine, review the session transcripts, and check what changed
- B. Nothing
- C. Only change the claude.ai password
- D. Reinstall Claude Code

<details><summary>Answer</summary>

**Answer: A** - Anything the session could reach is potentially exposed.

</details>

### Q4. How do you make sure this machine can never be published again?

- A. Uninstall the app on the phone
- B. Unset remoteControlAtStartup
- C. Set disableRemoteControl in managed (or user) settings on that machine
- D. Use --spawn session

<details><summary>Answer</summary>

**Answer: C** - disableRemoteControl turns the feature off entirely on that machine.

</details>
