---
type: lesson
title: "One command automations"
minutes: 19
---

An automation is worth having when the chore is real, repeats, and has an output you can check. Most of the work isn't the agent. It's the deterministic code around the agent that decides what it sees and whether its answer is accepted.

## The shape that holds up

```text
gather (deterministic)  →  agent step (headless)  →  verify (deterministic)  →  publish (atomic)
  grep, jq, git log         claude -p, few tools       grep, tests, schema        mv into place
```

| Stage | Rule |
|---|---|
| **Gather** | Do the counting, filtering and sorting with ordinary tools. Hand the agent a small digest, not raw megabytes. It's cheaper, faster and reproducible |
| **Skip** | If there's nothing to do (no errors today), write the trivial output yourself and **don't call the model** |
| **Agent step** | `claude -p`, with the input on stdin, the fewest tools that work (`--tools ""` for pure text tasks) and `--max-turns` as a ceiling |
| **Verify** | Check the output against facts you already computed. Did the report mention every top item from the digest? Does it start with the right heading? |
| **Publish** | Write to a scratch file, then `mv` it into place only after it passes, so a bad run never overwrites yesterday's good report |
| **Exit code** | 0 when published; non-zero with a reason on stderr when not. Cron, CI and your shell all understand that |

## Picking the chore

Good first automations share three traits:

1. You've done the chore by hand at least five times.
2. Its input is already on disk or one command away.
3. You can state what a correct output must contain.

A daily error-log digest, release notes from merged PRs, a weekly dependency report, and triage labels for new issues all qualify. "Improve the codebase" doesn't. There's nothing to verify.

## Running it unattended

```bash
# crontab -e
30 7 * * 1-5  cd /srv/ops && ./flow.sh /var/log/app "$(date +\%F)" >> flow.log 2>&1
```

- A cron job has a minimal `PATH` and none of your shell setup. Use absolute paths, or set `PATH` at the top of the script.
- Keep credentials in the environment the job runs with, never in the script.
- `set -euo pipefail` makes unexpected failures stop the script instead of publishing half a result.

## Commands this node introduces

`claude -p ... < input`, `--tools ""`, `--max-turns`, the gather-agent-verify-publish shape, and `mv` as an atomic publish.
