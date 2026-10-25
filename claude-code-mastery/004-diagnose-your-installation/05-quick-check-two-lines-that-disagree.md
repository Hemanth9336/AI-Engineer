---
type: quiz
title: "Quick check: two lines that disagree"
minutes: 8
---

### Q1. `claude --version` prints 2.1.310 but `claude doctor` says `Running: npm-global (2.1.240)`. What is the most likely cause?

- A. Two installs exist and different commands are reaching different binaries
- B. The model gateway is down
- C. doctor always lags one release behind
- D. The settings file is invalid

<details><summary>Answer</summary>

**Answer: A** - A mismatch means two builds are installed; PATH order, an alias, or a cached shell hash picks which one runs.

</details>

### Q2. Which command lists every `claude` your shell could run?

- A. claude --list
- B. type -a claude
- C. claude doctor --all
- D. ls ~/.claude

<details><summary>Answer</summary>

**Answer: B** - type -a shows aliases, functions, and every match on PATH in order.

</details>

### Q3. Your baseline script finds the versions disagree. What should it do?

- A. Print a warning and exit 0 so it never breaks a pipeline
- B. Delete the older install
- C. Silently pick the newer version
- D. Print MISMATCH and exit non-zero

<details><summary>Answer</summary>

**Answer: D** - A non-zero exit lets scripts and people notice the problem instead of trusting a broken baseline.

</details>

### Q4. What does `claude doctor` do that `/doctor` inside a session does not?

- A. It applies fixes automatically
- B. It needs a model call
- C. It audits CLAUDE.md content
- D. It works even when a session cannot start, because it runs from the shell

<details><summary>Answer</summary>

**Answer: D** - claude doctor is a read-only shell report; /doctor runs inside a session and can propose and apply fixes.

</details>
