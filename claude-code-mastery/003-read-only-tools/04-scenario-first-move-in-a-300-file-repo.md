---
type: scenario
title: "Scenario: first move in a 300-file repo"
minutes: 9
---

You join a team and are asked to find where invoice totals are rounded in a 300-file Python service you have never opened. You start a fresh Claude Code session in the repo root.

### Q1. What is the best first prompt?

- A. "Find where invoice totals are rounded: search for round( and total in the invoice code, then show me the function"
- B. "Read every file and summarize the codebase"
- C. "Refactor the rounding to use Decimal"
- D. "Tell me what you think of this code"

<details><summary>Answer</summary>

**Answer: A** - A targeted search answers the actual question without reading 300 files into context.

</details>

### Q2. You want the agent to look but not touch while it explores. What do you launch?

- A. claude --dangerously-skip-permissions
- B. claude with no flags, then approve every edit
- C. claude -p "..." --permission-mode acceptEdits
- D. claude -p "..." --allowedTools "Read Grep Glob"

<details><summary>Answer</summary>

**Answer: D** - Pre-approving only the read-only tools means nothing else can run in a headless session.

</details>

### Q3. The agent reports "rounding happens in billing/totals.py:round_invoice". What do you do before acting on it?

- A. Nothing - agents do not make up file names
- B. Ask the agent if it is sure
- C. Confirm it with one command, such as grep -n "def round_invoice" billing/totals.py
- D. Open a pull request immediately

<details><summary>Answer</summary>

**Answer: C** - Every factual claim should be checked against the source - it takes one command.

</details>
