---
type: lesson
title: "Site permissions, organization policy, and plan mode"
minutes: 14
---

## Site permissions

Per-site permissions come from the **Chrome extension's** settings, and Claude asks before acting on a site you haven't allowed. In VS Code the permission card offers to allow the site. Your Claude Code permission rules still apply on top. In auto mode, when the classifier approves a browser call, the extension skips its own per-site check, unless your permission rules deny sites to Claude in Chrome.

## Plan mode

Plan mode is for reading and planning, so browser actions with side effects ask first:

> "In plan mode, a permission prompt appears before Claude records a GIF, opens a new tab, or runs a shortcut."

Claude can still look at pages that are already open to inform the plan.

## Uploads, GIFs and data

- **Uploads:** Claude Code reads the file and sends its contents to the page. The session must be allowed to `Read` the file. The limit is 10 MB per upload, and credential-named files (`.env`, `*.pem`, `*.key`, anything under `.ssh`) are refused.
- **GIF recordings** capture everything visible, including account details on logged-in pages. Review them before sharing.
- JavaScript dialogs (`alert`, `confirm`) block the browser until you dismiss them.

## Organization policy

| Lever | Effect |
|---|---|
| `deniedMcpServers` including `claude-in-chrome` | No browser tools, and no install prompt |
| A managed MCP set without it | The same |
| An IP allowlist blocking `bridge.claudeusercontent.com` | The extension can't connect ("Browser extension is not connected") |
| The HIPAA organization toggle | Off by default |

## Commands this node introduces

Extension site permissions, plan-mode prompts for tabs, GIFs and shortcuts, the upload rules, and `deniedMcpServers` for `claude-in-chrome`.
