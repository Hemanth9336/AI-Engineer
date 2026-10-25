---
type: lesson
title: "The transport and the trust boundary"
minutes: 14
---

## What crosses the network

> "Your local Claude Code session makes outbound HTTPS requests only and never opens inbound ports on your machine."

- The session registers with the Anthropic API and polls for work. Your devices receive messages over a streaming connection routed through Anthropic, over TLS. It uses several short-lived credentials, each scoped to one purpose.
- **While Remote Control is connected, the session transcript (your messages, Claude's responses and tool activity) is stored on Anthropic servers.** That's how devices stay in sync and reconnect.
- **Execution and filesystem access stay on your machine.** Files you attach from the phone are downloaded to the machine and passed as `@` references.

## Who can drive

The session appears only in **your own** claude.ai account's apps. Anyone who can use your claude.ai account on any device can type into a session that runs with *your* local permissions, tools and credentials. That makes the account and its devices part of your machine's trust boundary.

| Control | What it does |
|---|---|
| Permission mode of the session | Remote prompts still go through it. A session started in `bypassPermissions` lets a phone run anything |
| **Trusted Devices** (beta) | Requires an enrolled device with a recent sign-in and a biometric step-up before driving. It's opt-in. Team and Enterprise Owners turn it on for the organization |
| `disableRemoteControl` (managed or user settings) | Turns Remote Control off on the machine entirely |
| `remoteControlAtStartup` | Auto-connect every session. Project and local settings can only turn it *off*: a checked-in file can't turn it on for everyone |
| The organization toggle | Off by default on Team and Enterprise |

## Hygiene

- Publish a session in **Manual** or **Accept edits** mode, not bypass.
- Name sessions so you know which machine you're steering.
- Stop the server (or `/remote-control` again to disconnect) when you're done. A forgotten server is an open door into your workstation through your account.
- On a remote host over SSH, run it inside `tmux` or `screen`, because the process has to keep running.

## Commands this node introduces

The outbound-only transport, the stored transcript, Trusted Devices, `disableRemoteControl`, and `remoteControlAtStartup`.
