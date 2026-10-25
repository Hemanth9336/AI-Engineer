---
type: scenario
title: "Scenario: rolling out agents to 200 developers"
minutes: 9
---

You're rolling Claude Code out to 200 developers on managed Macs (Jamf) and a Linux CI fleet. Security requires: no reading credentials, no bypass mode, approved models only, telemetry on, and plugins only from the internal marketplace. Inference must stay in your AWS account in eu-central-1.

### Q1. How do you deliver policy to both the Macs and the CI hosts?

- A. Commit .claude/settings.json in every repo
- B. ~/.claude/settings.json on each machine
- C. An email asking people to configure it
- D. A Jamf configuration profile for the Macs and /etc/claude-code/managed-settings.json baked into the CI image

<details><summary>Answer</summary>

**Answer: D** - Use the managed mechanism each platform supports; repo and user settings can be edited by developers.

</details>

### Q2. Which keys enforce "no bypass mode" and "only our permission rules"?

- A. defaultMode: plan
- B. forceLoginMethod
- C. disableAllHooks
- D. permissions.disableBypassPermissionsMode: "disable" and allowManagedPermissionRulesOnly: true

<details><summary>Answer</summary>

**Answer: D** - One removes the escape hatch; the other makes repo and user rules irrelevant.

</details>

### Q3. Inference must stay in your AWS account in Frankfurt. What goes in the managed env?

- A. ANTHROPIC_BASE_URL=https://api.anthropic.com
- B. CLOUD_ML_REGION=eu
- C. Only AWS_PROFILE
- D. CLAUDE_CODE_USE_BEDROCK=1, AWS_REGION=eu-central-1, and pinned eu. model IDs for every alias

<details><summary>Answer</summary>

**Answer: D** - The switch, the region, and pins together; without pins aliases follow Claude Code's built-in defaults.

</details>

### Q4. A repo contains a hook that uploads files to an external server. What stops it on managed machines?

- A. Nothing
- B. Code review
- C. availableModels
- D. allowManagedHooksOnly: true - only hooks from managed settings run

<details><summary>Answer</summary>

**Answer: D** - Repo hooks run commands on the developer's machine; lock them down centrally.

</details>

### Q5. How do you confirm a given laptop actually applies the policy?

- A. Ask the developer
- B. Look at the bill
- C. Check Jamf only
- D. Run /status on it: it names the managed source in use; then try a denied action

<details><summary>Answer</summary>

**Answer: D** - /status shows which managed source won, which is where most rollout bugs show up.

</details>
