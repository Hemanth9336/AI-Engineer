---
type: lesson
title: "Session names, push notifications, and when to reach for it"
minutes: 14
---

## Names

The title shown on your devices comes from, in order:
1. `--name`, `--remote-control "<name>"` or `/remote-control <name>`;
2. `/rename`;
3. the last meaningful message;
4. an auto-generated `hostname-adjective-animal` (set its prefix with `--remote-control-session-name-prefix` or `CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX`).

Name sessions after the machine and the task: `buildbox: flaky-tests`.

## Push notifications

With the Claude mobile app signed in to the same account, `/config` has two toggles: **Push when Claude decides** (for example, a long task finished) and **Push when actions required** (a permission prompt is waiting). You can also just ask: "notify me when the tests finish". Notifications are skipped while you're typing in the connected terminal. Forwarded dialogs expire after five minutes.

## What works remotely

Most conversation commands work from the phone or browser: `/compact`, `/clear`, `/context`, `/usage`, `/model`, `/effort`, `/fast`, `/rename`, `/config` and more. Some stay local-only, such as `/plugin` and `/resume`. Picking a model or effort from a device applies to the running session.

## When to reach for it

| You want | Use |
|---|---|
| To keep steering a session on *your* machine (local repo, internal network, local MCP servers) from a phone or another computer | **Remote Control** |
| Work to keep running when your laptop is closed, on someone else's machine | A **cloud session** (`claude --cloud`, topic 076) |
| A session on a remote server you SSH into | Desktop's SSH environment, or Remote Control on that server under tmux |
| Many concurrent sessions on one workstation, started from your phone | `claude remote-control --spawn worktree --capacity N` |

## Commands this node introduces

The session title order, `--remote-control-session-name-prefix`, the push notification toggles in `/config`, the commands available remotely, and choosing Remote Control vs cloud sessions.
