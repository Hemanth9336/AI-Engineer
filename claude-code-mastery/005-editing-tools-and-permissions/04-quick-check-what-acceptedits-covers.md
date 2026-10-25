---
type: quiz
title: "Quick check: what acceptEdits covers"
minutes: 9
---

### Q1. In `acceptEdits` mode, which of these still asks (or is denied in -p)?

- A. Editing src/app.py in the working folder
- B. Running mkdir build in the working folder
- C. Running python3 -m unittest
- D. Creating notes.md in the working folder

<details><summary>Answer</summary>

**Answer: C** - acceptEdits approves file edits and common filesystem commands; other commands such as running tests still need a rule.

</details>

### Q2. A headless fix ran with `--permission-mode acceptEdits`. Which edit is still not auto-approved?

- A. README.md
- B. .git/config
- C. src/utils.py
- D. tests/test_utils.py

<details><summary>Answer</summary>

**Answer: B** - .git is a protected path; acceptEdits never auto-approves writes there.

</details>

### Q3. Your `-p` run returned `subtype: success` but the file is unchanged. What do you check first?

- A. permission_denials in the envelope
- B. The model's temperature
- C. The session id
- D. duration_ms

<details><summary>Answer</summary>

**Answer: A** - In a headless run anything that would prompt is denied, and the envelope lists each denial.

</details>

### Q4. Why does the agent Read a file before editing it?

- A. Read approves the edit
- B. Reads are cheaper than edits
- C. It always reads every file in the folder
- D. Edit requires a prior Read so the replacement is anchored to the file's current content

<details><summary>Answer</summary>

**Answer: D** - Edit replaces an exact string and refuses to run on a file it has not read in the session.

</details>
