---
type: quiz
title: "Quick check: browser tools while planning"
minutes: 9
---

### Q1. In plan mode, Claude wants to open a new tab to check the docs page. What happens?

- A. It opens silently
- B. It's impossible
- C. A permission prompt appears first - opening tabs, recording GIFs, and shortcuts ask in plan mode
- D. It switches to auto mode

<details><summary>Answer</summary>

**Answer: C** - Plan mode keeps side effects behind a prompt.

</details>

### Q2. A repo sets `CLAUDE_CODE_ENABLE_CFC=1` in `.claude/settings.json`. Does Chrome turn on?

- A. Yes
- B. Only with --chrome
- C. Only in VS Code
- D. No - Claude Code ignores it: a project can't connect Claude to your browser

<details><summary>Answer</summary>

**Answer: D** - Only you can turn it on, with /chrome or --chrome.

</details>

### Q3. You authenticate with an API key. You pass `--chrome`. Result?

- A. Chrome works
- B. Chrome integration stays off; it needs a claude.ai sign-in
- C. It prompts for the key
- D. It uses Edge

<details><summary>Answer</summary>

**Answer: B** - The extension can't authenticate with API keys.

</details>

### Q4. Which Desktop feature tests your own app without any of your saved logins?

- A. The Desktop browser pane, which uses a clean profile
- B. Claude in Chrome
- C. Remote Control
- D. Artifacts

<details><summary>Answer</summary>

**Answer: A** - Use Claude in Chrome only when you need your real logins.

</details>

### Q5. What turns the browser tools off for a whole organization?

- A. Adding the claude-in-chrome server to deniedMcpServers in managed settings
- B. A memo
- C. disableAllHooks
- D. availableModels

<details><summary>Answer</summary>

**Answer: A** - Managed MCP policy controls the browser server like any other.

</details>
