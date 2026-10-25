---
type: lesson
title: "Cloud environments and auto-fix pull requests"
minutes: 14
---

## Environments

Each cloud session runs in an **environment**: the network policy, environment variables and setup script for its VM (Ubuntu 24.04, with about 4 vCPUs, 16 GB of RAM and 30 GB of disk).

| Network access | Outbound |
|---|---|
| **None** | Nothing through the session network. The Anthropic API is still reachable, which may let data leave the VM |
| **Trusted** (the default) | Allowlisted package registries, GitHub, cloud SDKs |
| **Full** | Any domain |
| **Custom** | Your allowlist, optionally plus the defaults |

- **Environment variables** (`.env` format) are readable by anyone who uses the environment. **Don't put secrets there.** Use **network secrets**: a proxy attaches the key to matching requests *after* they leave the VM, so the session never sees it.
- **Setup scripts** run as root before Claude Code starts. They must exit 0, and are cached as a snapshot if they finish within about five minutes. Install your toolchain there.
- **Git credentials stay outside the VM.** A GitHub proxy authenticates with scoped credentials. It rejects branch deletions and tag pushes, and blocks `gh pr` and `gh issue` GraphQL calls.
- **What doesn't carry over** from your machine: `~/.claude`, user plugins, user- and local-scope MCP servers, interactive SSO.

## Auto-fix pull requests

With the Claude GitHub App installed on the repo, a cloud session can **watch a PR**. It investigates CI failures and review comments, and pushes fixes. It asks when a request is ambiguous. Start it from the session's Changes card (**Auto-fix**), with `/autofix-pr` in the terminal on the PR branch, or by telling Claude to auto-fix a PR URL.

- Replies on GitHub use **your** GitHub account, labelled as coming from Claude Code. Comment-triggered automation (Atlantis, `issue_comment` Actions) can fire on them.
- GitHub sends no webhook when the base branch moves and creates a conflict, so auto-fix can't react to merge conflicts on its own.

## Commands this node introduces

Network access levels, network secrets, setup scripts, the GitHub proxy, `/autofix-pr`, and `/web-setup` (to connect your `gh` token).
