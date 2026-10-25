---
type: scenario
title: "Scenario: the review finds a real password"
minutes: 11
---

The review flags `DB_PASSWORD = "..."` in `shop/config.py`, and the value turns out to be the real production password. The file has been in the repo for a year.

### Q1. What is the first thing to do?

- A. Delete the line and push
- B. Ask Claude to obfuscate it
- C. Make the repo private
- D. Rotate the password (change it in the database), then remove it from the code

<details><summary>Answer</summary>

**Answer: D** - Anyone with a clone or a backup already has the old value; only rotation makes it useless.

</details>

### Q2. After moving it to `SHOP_DB_PASSWORD`, is the old value still exposed?

- A. No
- B. Yes, in git history, forks, CI logs, and caches, which is exactly why rotation comes first
- C. Only on GitHub
- D. Only for admins

<details><summary>Answer</summary>

**Answer: B** - Rewriting history is optional cleanup; rotation is the fix.

</details>

### Q3. The review report and the chat transcript contain the value. What should you have asked for?

- A. Findings that cite file and line but never the value
- B. Nothing different
- C. Encrypted transcripts
- D. A shorter report

<details><summary>Answer</summary>

**Answer: A** - Reports travel into tickets and chats; locations are enough to act on.

</details>

### Q4. How do you keep this from coming back?

- A. Trust reviewers
- B. Add a secret scanner (and push protection) to CI, plus a test that config reads the environment
- C. Ban the word password
- D. Review once a year

<details><summary>Answer</summary>

**Answer: B** - Automated gates catch the next one before it merges.

</details>
