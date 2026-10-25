---
type: quiz
title: "Quick check: where standing instructions live"
minutes: 9
---

### Q1. Your team wants every session in a repo to know `make check` runs lint and tests. Where does that go?

- A. ./CLAUDE.md, committed
- B. ~/.claude/CLAUDE.md
- C. ./CLAUDE.local.md
- D. A prompt you paste each time

<details><summary>Answer</summary>

**Answer: A** - Project instructions shared with the team live in the project CLAUDE.md under version control.

</details>

### Q2. You start claude in repo/services/api. Which CLAUDE.md files load at launch?

- A. Only repo/services/api/CLAUDE.md
- B. repo/services/api/CLAUDE.md and those in repo/services and repo
- C. Every CLAUDE.md in the repo
- D. Only the repo root file

<details><summary>Answer</summary>

**Answer: B** - Files in the working folder and every parent load at launch; subdirectory files load on demand.

</details>

### Q3. A rule must never be broken - the agent may not edit migrations/. Where should it be enforced?

- A. A deny rule or a PreToolUse hook
- B. In CLAUDE.md, in capital letters
- C. In the README
- D. In MEMORY.md

<details><summary>Answer</summary>

**Answer: A** - CLAUDE.md is guidance the model reads; permissions and hooks are enforced by Claude Code itself.

</details>

### Q4. Which line is the most useful CLAUDE.md rule?

- A. Write good code
- B. Run `python3 -m unittest` and report the result before finishing
- C. Be careful with the database
- D. Follow best practices

<details><summary>Answer</summary>

**Answer: B** - A specific, checkable command is something the agent can act on and a reviewer can verify.

</details>
