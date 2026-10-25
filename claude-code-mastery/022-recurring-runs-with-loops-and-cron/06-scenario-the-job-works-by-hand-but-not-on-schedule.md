---
type: scenario
title: "Scenario: the job works by hand but not on schedule"
minutes: 6
---

You wrote `nightly.sh`, which runs `claude -p` over your repo and writes a report. Run by hand it works every time. Under cron, `reports/` stays empty, and there is no error anywhere.

### Q1. Why is there no error anywhere?

- A. cron hides errors by design
- B. The crontab line does not redirect output, so cron's stdout and stderr go to local mail or nowhere
- C. claude -p never errors
- D. The report folder is read-only

<details><summary>Answer</summary>

**Answer: B** - Without >> log 2>&1, failures under cron leave no visible trace.

</details>

### Q2. After adding a log, it says `claude: command not found`. Fix?

- A. Set PATH inside the script (or use the absolute path to claude)
- B. Reinstall Claude Code
- C. Run cron as root
- D. Add claude to CLAUDE.md

<details><summary>Answer</summary>

**Answer: A** - cron's PATH is minimal; the script must set its own.

</details>

### Q3. Now claude runs but fails to authenticate. Why?

- A. The key expired at night
- B. Headless runs cannot authenticate
- C. cron does not read ~/.bashrc, so the API settings it exports are missing - source them in the script
- D. The model is offline at 2am

<details><summary>Answer</summary>

**Answer: C** - Anything your shell profile exports has to be loaded explicitly in the wrapper.

</details>

### Q4. How do you catch this class of bug before the next night?

- A. Wait and see
- B. Run it in tmux
- C. Rehearse with env -i HOME=$HOME /bin/sh -c ./nightly.sh
- D. Use --verbose

<details><summary>Answer</summary>

**Answer: C** - env -i reproduces cron's empty environment on demand.

</details>
