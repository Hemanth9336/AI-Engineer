---
type: quiz
title: "Quick check: what the digest guarantees"
minutes: 9
---

### Q1. An archive entry has a correct `sha256`. What does that guarantee?

- A. The installed zip is byte-for-byte the one whose digest you recorded
- B. The plugin is safe
- C. The publisher is Anthropic
- D. The plugin passed validation

<details><summary>Answer</summary>

**Answer: A** - A digest is integrity, not safety: it ties the install to bytes someone (hopefully) reviewed.

</details>

### Q2. An entry uses `"ref": "v1.0.0"` and no `sha`. The tag is deleted and re-created on a new commit. What do users get on update?

- A. The original v1.0.0 content
- B. Nothing changes
- C. An install error
- D. The new commit the tag now points at

<details><summary>Answer</summary>

**Answer: D** - Tags are mutable pointers; only a commit sha pins content.

</details>

### Q3. Upstream `main` gains a risky hook. Your entry pins `sha` to the reviewed commit. `claude plugin update` reports...

- A. updated
- B. conflict
- C. failed
- D. up_to_date

<details><summary>Answer</summary>

**Answer: D** - With a pin, upstream changes don't reach users until someone edits the catalog.

</details>

### Q4. Validation says `Must be a full 40-character lowercase git commit SHA`. Why not allow a short sha?

- A. Performance
- B. No reason
- C. GitHub requires it
- D. A short prefix can become ambiguous, and it isn't an exact identity

<details><summary>Answer</summary>

**Answer: D** - Pins must identify exactly one commit forever.

</details>

### Q5. Who should be allowed to change a pinned sha in the team marketplace?

- A. Anyone, automatically
- B. The plugin author alone
- C. A reviewer, after reading the diff between the old and new commits
- D. CI on every upstream push

<details><summary>Answer</summary>

**Answer: C** - Moving the pin is the trust decision; treat it like merging code.

</details>
