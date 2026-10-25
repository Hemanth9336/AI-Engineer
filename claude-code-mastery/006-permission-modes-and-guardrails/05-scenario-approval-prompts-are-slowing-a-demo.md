---
type: scenario
title: "Scenario: approval prompts are slowing a demo"
minutes: 7
---

You are demoing Claude Code on your work laptop to a customer. It is fixing a bug in your team's repo, and every edit and test run stops for approval. A colleague whispers: "just restart it with --dangerously-skip-permissions".

### Q1. What is the best way to cut the prompts for this demo?

- A. Restart with --dangerously-skip-permissions
- B. Delete .claude/settings.json
- C. Turn off the trust dialog in ~/.claude.json
- D. Switch to acceptEdits with Shift+Tab and allow the test command with a rule

<details><summary>Answer</summary>

**Answer: D** - acceptEdits plus one allow rule removes the noisy prompts while keeping everything else under review.

</details>

### Q2. Why is bypassPermissions wrong here?

- A. It is slower
- B. It only works with opus
- C. It disables the model
- D. It runs everything with your full access on a machine with credentials and network - it belongs in disposable containers

<details><summary>Answer</summary>

**Answer: D** - bypassPermissions removes the checks entirely, so it is only safe where the blast radius is a throwaway environment.

</details>

### Q3. The repo has a .env with real keys. Which settings protect it even in auto mode?

- A. An allow rule for Read(./.env)
- B. A deny rule Read(./.env), plus sandbox denyRead for shell commands
- C. Plan mode
- D. Setting defaultMode to acceptEdits

<details><summary>Answer</summary>

**Answer: B** - Deny rules apply in every mode; the sandbox entry covers commands like cat that the Read rule does not.

</details>
