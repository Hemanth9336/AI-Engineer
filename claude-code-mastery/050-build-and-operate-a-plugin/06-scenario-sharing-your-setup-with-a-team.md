---
type: scenario
title: "Scenario: sharing your setup with a team"
minutes: 7
---

You've tuned a set of skills, a hook, and an MCP server in your own `~/.claude/`. Five teammates want the same setup, and two of them need a different Jira URL and their own API token.

### Q1. What is the most maintainable way to share it?

- A. Zip ~/.claude and send it
- B. Paste the files into the team wiki
- C. Package the pieces as a plugin with a manifest and version, and publish it in a marketplace
- D. Commit your ~/.claude to every repo

<details><summary>Answer</summary>

**Answer: C** - A versioned plugin can be validated, installed with one command, updated, and removed cleanly.

</details>

### Q2. How do teammates supply their own Jira URL and token?

- A. Edit the plugin files
- B. Hard-code yours
- C. Environment variables in CLAUDE.md
- D. userConfig options: a string for the URL and a sensitive string for the token

<details><summary>Answer</summary>

**Answer: D** - Sensitive values go to the OS credential store, never into settings.json or the repo.

</details>

### Q3. Should the token reach the MCP server through `${user_config.jira_token}` in `.mcp.json`?

- A. No, never
- B. Yes; MCP server config substitutes user config values
- C. Only for http servers
- D. Only in skills

<details><summary>Answer</summary>

**Answer: B** - MCP and LSP config, and exec-form hook args, receive user config; shell-form commands don't.

</details>

### Q4. You want the plugin on for everyone who clones `payments-api`, but not in other repos. Which scope?

- A. user
- B. project, which writes .claude/settings.json in that repo
- C. local
- D. managed

<details><summary>Answer</summary>

**Answer: B** - Project scope is shared through git; user scope would turn it on everywhere for one person.

</details>

### Q5. You changed a hook and bumped the version. How do teammates get it?

- A. Reinstall from scratch
- B. Edit their cache folders
- C. Nothing; plugins live-reload from your machine
- D. Refresh the marketplace and run claude plugin update (or let auto-update run), then /reload-plugins

<details><summary>Answer</summary>

**Answer: D** - Updates compare versions; a running session picks up the new copy after /reload-plugins or a restart.

</details>
