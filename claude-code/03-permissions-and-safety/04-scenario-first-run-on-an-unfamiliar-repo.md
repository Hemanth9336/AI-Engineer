---
type: scenario
title: "Scenario: first run on an unfamiliar repo"
minutes: 4
---

You've just cloned a contractor's repository. It has a `Makefile` with a `deploy` target, a `scripts/` folder full of shell scripts you haven't read, and a `.env.production` file. Your manager wants a summary of how the code is organized and a list of risky spots, today.

### Q1. How do you start Claude Code on this repo?

- A. Copy the repo into your home directory and run `claude` there
- B. `claude --permission-mode bypassPermissions` so it can run the scripts and see what they do
- C. `claude -p "fix everything" --permission-mode acceptEdits`
- D. `claude --permission-mode plan` in the repo, and ask for a read-only tour and a risk list

<details><summary>Answer</summary>

**Answer: D** - Plan mode reads and proposes but changes nothing - right for code you don't trust yet.

</details>

### Q2. Claude asks to run `make deploy` "to understand the deploy flow". What do you do?

- A. Choose Yes once
- B. Choose Yes, and don't ask again
- C. Choose No and ask it to read the Makefile and scripts instead
- D. Switch to bypassPermissions

<details><summary>Answer</summary>

**Answer: C** - Reading explains the deploy; running it deploys.

</details>

### Q3. You'll work in this repo for weeks. Which rule belongs in its `.claude/settings.json` first?

- A. `"allow": ["Bash(*)"]`
- B. `"deny": ["Read(./.env.production)", "Bash(make deploy:*)"]`
- C. `"defaultMode": "bypassPermissions"`
- D. No rules - just be careful

<details><summary>Answer</summary>

**Answer: B** - Deny rules for secrets and deploys hold no matter who clicks what.

</details>
