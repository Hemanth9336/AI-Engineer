---
type: lesson
title: "The built-in Linux sandbox"
minutes: 12
---

Permission rules decide whether a command **runs**. The sandbox decides what a running command can **reach**. They are independent layers, and the sandbox is off by default.

## What it restricts

| Access | Sandboxed default |
|---|---|
| Writes | The working folder, a per-user temp dir, and added directories; protected paths stay denied |
| Reads | Most of the machine - including `~/.ssh` - unless you add `denyRead` entries |
| Network | No direct route out; a local proxy checks each host against `allowedDomains`, which starts empty |
| Environment | Inherited, secrets included, unless you scrub or mask credentials |

On Linux and WSL2 it is enforced with **bubblewrap** (filesystem) and **socat** (the network relay); install both with `apt install bubblewrap socat`. macOS uses its built-in Seatbelt framework.

## Turning it on

Run `/sandbox` in a session, or put it in settings:

```json
{
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "filesystem": { "denyRead": ["./.env"] },
    "network": { "allowedDomains": ["pypi.org", "files.pythonhosted.org"] }
  }
}
```

- `failIfUnavailable: true` - if bubblewrap is missing, Claude Code exits at startup instead of silently running commands **un**sandboxed.
- `allowUnsandboxedCommands: false` - strict mode: Claude cannot retry a blocked command outside the sandbox with `dangerouslyDisableSandbox`.
- Sandbox paths use plain conventions: `/abs`, `~/home-relative`, and `./` (or no prefix) relative to the project for project settings - different from the `//` and `/` prefixes of permission rules.

## What it does not cover

The sandbox wraps **shell commands**. Read, Edit, Write, and WebFetch follow permission rules instead, so a sandbox `denyRead` does not stop the Read tool - pair it with a `Read(./.env)` deny rule. Hooks, local MCP servers, and your status line command also run outside it. To put everything behind one boundary, run Claude Code itself in a container or VM.

## Two modes

In **auto-allow** mode, commands that run inside the sandbox are approved without a prompt (deny rules, content ask rules, and critical-path removals still apply). In **regular permissions** mode every command still goes through normal approvals, sandboxed or not.

## Commands this node introduces

`/sandbox` shows the sandbox status and switches its mode; `apt install bubblewrap socat` provides it on Linux.
