---
type: lesson
title: "The loop command and account-backed routines"
minutes: 10
---

Two built-in options repeat work without you writing a script.

## /loop: repeat inside a session

```text
/loop 5m check whether the deploy finished and tell me what happened
/loop 20m /review-pr 1234
/loop check the CI run for my branch
```

- With an interval, Claude turns it into a cron expression and schedules the prompt (units `s`, `m`, `h`, `d`; one-minute granularity).
- With no interval, Claude picks the delay each time based on what it saw.
- With no prompt, it runs a built-in maintenance prompt, or your `loop.md`.
- Ask Claude to cancel it - "cancel the deploy check loop". Esc does not stop a fixed-interval loop.

Loops are **session-scoped**: they live in the open session, are restored on `--resume`, and expire after seven days. Close the terminal and they stop.

## Cloud scheduled tasks (routines)

`/schedule daily PR review at 9am` creates a **cloud** task tied to your claude.ai account. It runs on Anthropic-managed infrastructure on a fresh clone of your repository - with your laptop off - and can also be triggered by an API call or a GitHub event. You manage them at claude.ai/code/routines.

| | `/loop` | cron + script | Cloud scheduled task |
|---|---|---|---|
| Survives closing the terminal | No | Yes | Yes |
| Survives the machine being off | No | No | Yes |
| Local files and tools | Yes | Yes | No - a fresh clone |
| Minimum interval | 1 minute | 1 minute | 1 hour |
| Needs | An open session | A machine you run | A claude.ai account |

Cloud tasks need an account sign-in, so this lab practises the cron path, which works with the lab gateway.

## Commands this node introduces

`/loop [interval] [prompt]` and `/schedule <description>`.
