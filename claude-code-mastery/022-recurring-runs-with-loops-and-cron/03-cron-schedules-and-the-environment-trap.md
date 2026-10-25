---
type: lesson
title: "Cron schedules and the environment trap"
minutes: 10
---

`cron` runs a command on a schedule:

```text
# m  h  dom mon dow  command
  0  2  *   *   *    /root/mastery/022-hygiene/hygiene.sh >> /root/mastery/022-hygiene/logs/cron.log 2>&1
```

That runs at 02:00 every day. Install it with `crontab -e` (or `crontab file.txt`) and list it with `crontab -l`.

## The trap

A command that works in your terminal often **fails under cron**, silently, because cron runs it with an almost empty environment:

| In your terminal | Under cron |
|---|---|
| `PATH` includes `~/.local/bin`, so `claude` is found | `PATH=/usr/bin:/bin` - `claude: not found` |
| `~/.bashrc` loaded your API settings | `.bashrc` is **not** read - no `ANTHROPIC_BASE_URL`, no key |
| You are in the project folder | The working directory is `$HOME` |
| Errors appear on screen | Output goes nowhere unless you redirect it |

## The fix: a self-contained wrapper script

```bash
#!/bin/bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
[ -f "$HOME/.config/ailab/env" ] && . "$HOME/.config/ailab/env"   # the lab's API settings
cd /root/mastery/022-hygiene                                      # absolute, always
mkdir -p reports logs
if ! mkdir /tmp/hygiene-022.lock 2>/dev/null; then echo "previous run still active"; exit 0; fi
trap 'rmdir /tmp/hygiene-022.lock' EXIT
claude -p "$(cat prompts/hygiene.md)" --max-turns 10 --output-format json > "reports/hygiene-$(date +%F).json"
```

- Every path is absolute; the script sets its own `PATH` and loads the settings `.bashrc` would have.
- The `mkdir` lock is atomic: a second copy started while the first runs exits immediately (`flock` does the same on Linux).
- The crontab line redirects stdout and stderr to a log, so failures leave evidence.

**Test it the way cron will run it**, before you trust the schedule:

```bash
env -i HOME="$HOME" /bin/sh -c /root/mastery/022-hygiene/hygiene.sh
```

`env -i` wipes the environment, which reproduces the trap on demand.

## Commands this node introduces

`crontab -e`, `crontab -l`, and `env -i HOME="$HOME" /bin/sh -c <script>` to rehearse a cron run.
