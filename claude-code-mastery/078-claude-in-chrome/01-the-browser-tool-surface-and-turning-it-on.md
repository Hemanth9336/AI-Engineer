---
type: lesson
title: "The browser tool surface and turning it on"
minutes: 14
---

**Claude in Chrome** gives Claude Code a real browser: your Chrome (or Edge, Brave, Arc, and other Chromium browsers) through the Claude in Chrome extension. Claude opens its own tabs in a visible window, grouped per session, and **shares your browser's login state**. When it hits a login page or a CAPTCHA, it pauses and asks you.

## Turning it on

```bash
claude --chrome          # for this session
/chrome                  # status, permissions, reconnect, pick a browser, or Enabled by default
```

| Requirement | Detail |
|---|---|
| Extension | Claude in Chrome, version 1.0.36 or later |
| Account | A Pro, Max, Team or Enterprise plan, signed in with `/login`. With an API key or a `claude setup-token` token, Chrome stays off even with `--chrome` |
| Provider | Not available through Bedrock, Agent Platform or Foundry |
| Platform | Not supported in WSL |
| Organization | The extension and Claude Code must be signed in to the same organization. On HIPAA Enterprise it's off until an Owner turns it on, and the BAA doesn't cover data sent to third-party sites |

- **Enabled by default** (in `/chrome`) loads the browser tools in every session, at a context cost.
- **A project can't turn it on.** `CLAUDE_CODE_ENABLE_CFC=1` in `.claude/settings.json` is ignored, because a repository you check out must not be able to connect Claude to your browser.
- Organizations can block it with `deniedMcpServers` (the `claude-in-chrome` server) or with a managed MCP set that doesn't allow it.
- List the tools with `/mcp` > `claude-in-chrome` > **View tools**.

## Commands this node introduces

`claude --chrome`, `/chrome`, Enabled by default, the `claude-in-chrome` MCP server, and `CLAUDE_CODE_ENABLE_CFC` (ignored in project settings).
