---
type: quiz
title: "Quick check: what a fix must come with"
minutes: 9
---

### Q1. You wrote a regression test after the fix, and it passes. What is missing?

- A. Evidence it fails without the fix - run it against the old code
- B. Nothing
- C. A second test
- D. Coverage

<details><summary>Answer</summary>

**Answer: A** - A test that was never red might not test the bug at all.

</details>

### Q2. Where should the expected value in a reproduction come from?

- A. The current output of the code
- B. Claude's guess
- C. An independent source: spec, hand count, or another tool
- D. The previous release

<details><summary>Answer</summary>

**Answer: C** - The code under suspicion can't be its own oracle.

</details>

### Q3. Why split the work into a test commit and a fix commit?

- A. Git requires it
- B. It makes the history longer
- C. A reviewer can see red at the first commit and green at the second
- D. It speeds CI up

<details><summary>Answer</summary>

**Answer: C** - Two commits turn 'trust me' into something anyone can re-run.

</details>

### Q4. The fix run made the test pass by changing its expected value. How do you prevent that?

- A. Ask nicely in the prompt
- B. Run it twice
- C. Write(tests/**) in deny
- D. --disallowedTools "Edit(tests/**)" for the fix run

<details><summary>Answer</summary>

**Answer: D** - A disallowed Edit rule blocks Write too; a Write() rule never matches.

</details>
