---
type: quiz
title: "Quick check: spotting nondeterminism"
minutes: 11
---

### Q1. A test compares `list(set(names))` with a fixed list. It fails about 70% of runs. Which variable explains it?

- A. PYTHONHASHSEED
- B. TZ
- C. The random module's seed
- D. Test order

<details><summary>Answer</summary>

**Answer: A** - Set order of strings follows their hashes, which Python randomizes per process.

</details>

### Q2. A test passes when run alone and fails in the full suite. The most likely cause?

- A. Hash ordering
- B. Shared state left behind by an earlier test
- C. The timezone
- D. Slow disk

<details><summary>Answer</summary>

**Answer: B** - Order-dependent tests leak state such as globals, files, or class attributes.

</details>

### Q3. Which is a real fix for a flaky ordering assertion?

- A. Retry the test 3 times
- B. Mark it skip
- C. Sort both sides of the assertion
- D. Make the code return the documented order

<details><summary>Answer</summary>

**Answer: D** - Sorting both sides would hide a broken 'first-seen order' contract.

</details>

### Q4. You found that seed 3 fails. Why is that valuable?

- A. It proves the code is fine
- B. It reproduces the flake on demand: PYTHONHASHSEED=3 python3 -m unittest
- C. It makes CI faster
- D. Seeds don't matter

<details><summary>Answer</summary>

**Answer: B** - A deterministic reproduction turns a flake into an ordinary bug.

</details>
