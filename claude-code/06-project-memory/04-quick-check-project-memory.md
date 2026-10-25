---
type: quiz
title: "Quick check: project memory"
minutes: 4
---

### Q1. When does Claude Code read the project's CLAUDE.md?

- A. Only after /init
- B. Only when you type /memory
- C. At the start of every session in that project
- D. Only if you mention it in the prompt

<details><summary>Answer</summary>

**Answer: C** - It's loaded automatically, every session.

</details>

### Q2. Where should "I prefer short answers without emojis" go?

- A. README.md
- B. The project's CLAUDE.md
- C. `~/.claude/CLAUDE.md` - it's your preference for every project
- D. .claude/settings.json

<details><summary>Answer</summary>

**Answer: C** - Personal preferences go in your user-level memory.

</details>

### Q3. Which line does NOT belong in CLAUDE.md?

- A. `Never edit migrations/ - add a new migration`
- B. `Run one test: python3 -m unittest tests.test_invoice`
- C. `STRIPE_KEY=sk_live_...` so Claude can test payments
- D. `Money is integer cents`

<details><summary>Answer</summary>

**Answer: C** - Never secrets: the file is committed and sent to the model.

</details>

### Q4. Claude keeps running `pytest`, but your project uses `./scripts/test.sh`. Best fix?

- A. Uninstall pytest
- B. Say it again in every prompt
- C. Add the test command under ## Commands in CLAUDE.md
- D. Switch models

<details><summary>Answer</summary>

**Answer: C** - A repeated mistake is a missing line in project memory.

</details>

### Q5. "Never read .env" is in CLAUDE.md. Is that enough to protect the file?

- A. Yes, if you write it in capitals
- B. Yes - Claude always obeys CLAUDE.md
- C. No - it's guidance; enforce it with a deny rule like Read(./.env)
- D. No - CLAUDE.md is ignored in -p mode

<details><summary>Answer</summary>

**Answer: C** - Memory guides; permissions enforce.

</details>
