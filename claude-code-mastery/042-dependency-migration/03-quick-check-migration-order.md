---
type: quiz
title: "Quick check: migration order"
minutes: 11
---

### Q1. The suite is red before you start the upgrade. What first?

- A. Upgrade anyway
- B. Ask Claude to upgrade and fix everything
- C. Delete the failing tests
- D. Get it green on the old version, so new failures mean the upgrade

<details><summary>Answer</summary>

**Answer: D** - Without a green baseline you can't attribute failures.

</details>

### Q2. When must you capture the golden output?

- A. After the migration
- B. Never; tests are enough
- C. Only if tests fail
- D. Before swapping the version

<details><summary>Answer</summary>

**Answer: D** - Once the new version is in, the old behavior is no longer available to record.

</details>

### Q3. Why point Claude at RELEASE_NOTES.md instead of saying "upgrade to v2"?

- A. The notes are the source of truth; the model's memory of the API may be out of date
- B. It is shorter
- C. Claude can't read code
- D. It avoids tests

<details><summary>Answer</summary>

**Answer: A** - Libraries change faster than training data.

</details>

### Q4. The golden diff shows one changed line, and the release notes say nothing about it. What do you do?

- A. Regenerate the golden file
- B. Treat it as a migration bug until you can explain it
- C. Ignore it
- D. Pin back to 1.x forever

<details><summary>Answer</summary>

**Answer: B** - Unexplained diffs are exactly what golden output exists to catch.

</details>
