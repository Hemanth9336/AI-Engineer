---
type: lesson
title: "Desktop session types and the permission selector"
minutes: 14
---

In the Claude Desktop app, Claude Code is the **Code** tab, next to chat and **Cowork**. It's an interactive surface, not a scripting one: there's no `-p` or `--output-format`.

## Where a session runs

| Session type | Claude runs | Good for |
|---|---|---|
| **Local** | On your machine, with direct file access | Everyday work in your repos |
| **Cloud** | On Anthropic-managed infrastructure (or your self-hosted environment). It keeps going when you close the app | Long tasks (topic 076) |
| **SSH** | On a remote machine over SSH | Servers and big dev boxes |
| **WSL** (Windows) | In a WSL 2 distribution | Linux toolchains on Windows |

Saved environments remember where a session runs (and, for local and SSH, which folders it uses). A local session can be sent to the cloud with **Open in** > **Cloud**. From the CLI, `/desktop` (or `claude --desktop`) opens the current session in the app.

## The permission selector

| Mode in the UI | Settings key | Behaviour |
|---|---|---|
| Manual | `default` | Asks before edits and commands, and shows the diff |
| Accept edits | `acceptEdits` | Auto-accepts file edits and common file commands, and asks for other commands |
| Plan | `plan` | Reads and proposes a plan without editing |
| Auto | `auto` | A classifier checks shell and network actions instead of routine prompts (supported models only; admins can set `disableAutoMode`) |
| Bypass permissions | `bypassPermissions` | No prompts. "Only use this in sandboxed containers or VMs." Pro and Max enable it in Settings; Team and Enterprise by organization policy |

- The default for new local sessions comes from `permissions.defaultMode` in your settings files, the same files the CLI uses.
- A pick in the selector is **remembered per folder** and outranks `defaultMode`, except Plan, which lasts for the current session only.
- Cloud sessions offer Accept edits, Plan and Auto. There's no Bypass in cloud sessions.

## Commands this node introduces

The Local, Cloud, SSH and WSL session types, saved environments, **Open in**, `/desktop`, the mode selector, `permissions.defaultMode`, and `disableAutoMode`.
