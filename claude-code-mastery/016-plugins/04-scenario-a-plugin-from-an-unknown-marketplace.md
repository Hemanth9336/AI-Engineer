---
type: scenario
title: "Scenario: a plugin from an unknown marketplace"
minutes: 9
---

A blog post recommends a "productivity" plugin. Installing it needs `claude plugin marketplace add some-user/cc-goodies`, a GitHub account you have never heard of. The plugin README says it "auto-formats your code and syncs your settings".

### Q1. What do you check before installing?

- A. Only the star count
- B. Nothing - plugins are sandboxed
- C. Whether it has an icon
- D. The plugin's hooks/hooks.json and .mcp.json - code that will run on your machine - and who publishes it

<details><summary>Answer</summary>

**Answer: D** - Hooks and MCP servers run with your permissions, outside the sandbox; read them and know the publisher.

</details>

### Q2. "Syncs your settings" is implemented by a SessionStart hook that runs `curl ... | sh`. What do you do?

- A. Install it at user scope
- B. Install it at project scope so teammates get it too
- C. Install and then run /sandbox
- D. Do not install it; report it if it seems malicious

<details><summary>Answer</summary>

**Answer: D** - A hook that downloads and executes remote code on every session start is a supply-chain risk.

</details>

### Q3. Your company wants engineers to install plugins only from the internal marketplace. How?

- A. Ask nicely in Slack
- B. Rename the official marketplace
- C. Delete ~/.claude/plugins nightly
- D. Managed settings that restrict known marketplaces (strictKnownMarketplaces)

<details><summary>Answer</summary>

**Answer: D** - Managed settings let administrators allowlist marketplaces for every user.

</details>
