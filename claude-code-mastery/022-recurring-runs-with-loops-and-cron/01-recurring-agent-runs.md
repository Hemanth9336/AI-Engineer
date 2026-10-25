---
type: lesson
title: "Recurring agent runs"
minutes: 10
---

Some agent work is worth doing on a cycle rather than on request: a nightly sweep for TODOs, a weekly dependency check, a morning summary of yesterday's merged PRs, a poll of a slow deploy.

## Four ways to repeat work

| Mechanism | Runs where | Needs an open session? | Good for |
|---|---|---|---|
| A **shell loop** around `claude -p` | Your machine | No | Repeating a task N times or until a condition |
| **cron** (or systemd timers) running a script | Your machine | No | Fixed schedules on a server you control |
| **`/loop`** inside a session | Your machine | **Yes** | Polling while you work: "check the deploy every 5m" |
| **Cloud scheduled tasks** (`/schedule`) | Anthropic's cloud, on a fresh clone | No | Schedules that survive your laptop being off |

## What every recurring run needs

- **A fixed prompt in a file** - the same instructions every time (topic 013).
- **Headless output** - `--output-format json`, written to a dated file.
- **Pre-approved tools only** - nobody is there to answer a prompt; anything that would ask is denied.
- **A bound** - `--max-turns`, a timeout, or a loop counter, so a confused run cannot spin forever.
- **No overlap** - a lock, so tonight's run does not start while last night's is still going.
- **A place to look** - a log file and the dated reports.

## Read-only by default

A nightly job you do not watch should **report**, not **change**: list the TODOs, open an issue, write a markdown report. Changes go through a human or a reviewed pull request. If a recurring job must edit, it works on a branch or worktree, never on `main`.

## Commands this node introduces

`--max-turns <n>` bounds a headless run's loop; `date +%F` names a daily report.
