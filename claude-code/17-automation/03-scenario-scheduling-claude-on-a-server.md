---
type: scenario
title: "Scenario: scheduling Claude on a server"
minutes: 5
---

Your team wants a nightly job on a shared Linux server: Claude reads the day's error log, groups the errors, and writes a report to a shared folder. A colleague's first draft runs `claude -p "analyze the logs and fix anything you can" --permission-mode bypassPermissions` from cron.

### Q1. What's the most serious problem with the draft?

- A. bypassPermissions plus "fix anything" lets an unattended agent change a shared server with nobody watching
- B. It doesn't use haiku
- C. It should run in the morning
- D. It doesn't use stream-json

<details><summary>Answer</summary>

**Answer: A** - Unattended runs get the least privilege, not the most.

</details>

### Q2. Which command fits the job?

- A. `claude --permission-mode bypassPermissions`
- B. `claude -p "read every log on the server"`
- C. `tail -n 2000 /var/log/app/error.log | claude -p "Group these errors by cause..." --max-turns 3 --output-format json`
- D. `claude` (interactive) from cron

<details><summary>Answer</summary>

**Answer: C** - Data on stdin, fixed prompt, bounded turns, parseable output, no write permissions needed.

</details>

### Q3. The job works in your terminal but produces nothing from cron. What's the likely cause?

- A. The log file is too small
- B. Claude doesn't work at night
- C. cron can't run bash
- D. cron's minimal environment - PATH (where claude and jq live) and the login/credentials the run needs aren't there

<details><summary>Answer</summary>

**Answer: D** - Use absolute paths and make sure the cron user has the environment and sign-in the job needs.

</details>

### Q4. How will you know when the nightly job fails?

- A. Claude will email you
- B. Check the folder every morning by hand
- C. The script exits non-zero and logs 'failed', and cron's output or monitoring alerts on it
- D. It can't fail

<details><summary>Answer</summary>

**Answer: C** - Exit codes and log lines turn silent failures into visible ones.

</details>
