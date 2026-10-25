---
type: lesson
title: "Claude in scripts"
minutes: 8
---

Headless Claude Code (`claude -p`) is a command like any other, so it fits wherever commands go: shell scripts, Makefiles, git hooks, cron jobs and CI pipelines. The trick is to write those scripts as carefully as any other automation - because nobody is watching when they run.

## The shape of a good Claude script

```bash
#!/usr/bin/env bash
set -euo pipefail

out="$(git log --since='24 hours ago' --oneline | claude -p "Summarize for the team update" \
        --max-turns 2 --output-format json)" || { echo "claude failed" >&2; exit 1; }
[ "$(jq -r '.is_error' <<<"$out")" = "false" ] || { echo "claude reported an error" >&2; exit 1; }
jq -r '.result' <<<"$out" > "reports/digest-$(date +%F).md"
```

| Habit | Why |
|---|---|
| `set -euo pipefail` | Stop at the first failure instead of writing garbage |
| `--output-format json` | Get `.result`, `.is_error`, cost and denials in one parseable object |
| Check the exit code **and** `.is_error` | A run can exit cleanly and still report an error |
| `--max-turns` | A confused run can't loop (and spend) forever |
| Minimal permissions | `--allowedTools` for exactly what the job needs - never `bypassPermissions` on a real server |
| Pipe data in, not instructions | Feed the commits or log lines on stdin; keep the prompt fixed |
| Write a log line every run | `ok`, `failed`, `skipped` - so you know it ran at all |
| Skip when there's nothing to do | No commits today? Don't call the model |

## Exit codes are your contract

Whatever runs your script - cron, CI, a Makefile - only understands exit codes. Return 0 when the job did its work (or correctly decided there was nothing to do) and non-zero when it didn't. Then failures show up as red builds or cron emails instead of silently missing reports.

## Keep cost and time bounded

- Use a small model for routine jobs: `--model haiku`.
- Send only what's needed: the last day's commits, not the whole history.
- `--max-turns` caps the steps; a `timeout 300 claude -p ...` wrapper caps wall-clock time.
- The JSON result includes `total_cost_usd` - log it and you'll notice when a job gets expensive.

## Where else this fits

- **git hooks** - a `prepare-commit-msg` hook that drafts a message from the staged diff.
- **CI** - review a pull request's diff and post the result as a comment (there's an official GitHub Action for Claude Code).
- **Make targets** - `make release-notes` runs your `/changelog` command headless.

In every case the rules are the same: fixed prompt, data on stdin, minimal permissions, bounded turns, checked results.
