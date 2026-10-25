---
type: quiz
title: "Quick check: publishing a fleet of workstations"
minutes: 9
---

### Q1. You want to start many sessions from your phone, each in its own checkout of one repo on your workstation. Which command?

- A. claude --rc
- B. /remote-control
- C. claude remote-control --spawn worktree --capacity 8
- D. claude --cloud

<details><summary>Answer</summary>

**Answer: C** - Server mode with worktree spawning gives each on-demand session its own git worktree.

</details>

### Q2. A repo's `.claude/settings.json` sets `remoteControlAtStartup: true`. Does every teammate's session auto-publish?

- A. Yes
- B. Only interactively
- C. Only on Team plans
- D. No - project and local settings can only turn auto-connect off, never on

<details><summary>Answer</summary>

**Answer: D** - A checked-in file can't publish everyone's sessions.

</details>

### Q3. A colleague's machine uses Bedrock through managed settings. Can they use Remote Control?

- A. Yes
- B. Only from Desktop
- C. Only with --rc
- D. No - Remote Control needs a claude.ai sign-in on the Anthropic API, not a cloud-provider or gateway setup

<details><summary>Answer</summary>

**Answer: D** - Remote Control isn't available on Bedrock, Agent Platform, Foundry, or gateways.

</details>

### Q4. While Remote Control is connected, where does the session transcript live?

- A. It's also stored on Anthropic servers so devices stay in sync; execution stays on your machine
- B. Only on your machine
- C. On the phone
- D. Nowhere

<details><summary>Answer</summary>

**Answer: A** - The transcript syncs; files and execution don't leave the machine.

</details>

### Q5. Your company wants Remote Control off on every managed laptop. What do you deploy?

- A. A memo
- B. crossSessionInbound: refuse
- C. --capacity 0
- D. disableRemoteControl in managed settings (and leave the organization toggle off)

<details><summary>Answer</summary>

**Answer: D** - Machine-level policy plus the org toggle.

</details>
