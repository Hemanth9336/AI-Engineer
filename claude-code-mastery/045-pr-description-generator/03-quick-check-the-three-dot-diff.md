---
type: quiz
title: "Quick check: the three-dot diff"
minutes: 11
---

### Q1. main gained a README change after you branched. Which command shows only your branch's changes?

- A. git diff main..HEAD
- B. git diff main...HEAD
- C. git diff HEAD
- D. git log main

<details><summary>Answer</summary>

**Answer: B** - Three dots diff against the merge base.

</details>

### Q2. What does `git diff main..HEAD` show for main's newer README line?

- A. Nothing
- B. An error
- C. It appears as added
- D. It appears as removed, as if your branch reverted it

<details><summary>Answer</summary>

**Answer: D** - Two dots compare the two tips, so main's newer work looks like your deletion.

</details>

### Q3. Which command lists exactly the commits your PR adds?

- A. git log main...HEAD
- B. git log main..HEAD
- C. git log HEAD..main
- D. git log --all

<details><summary>Answer</summary>

**Answer: B** - For log, two dots means reachable from HEAD but not from main.

</details>

### Q4. The model returns the label `urgent`, which your repo doesn't use. What should happen?

- A. Create the label
- B. Drop the label silently
- C. render_pr.py rejects the description and writes no PR.md
- D. Open the PR anyway

<details><summary>Answer</summary>

**Answer: C** - Fixed sets are enforced in code; nothing invalid reaches GitHub.

</details>
