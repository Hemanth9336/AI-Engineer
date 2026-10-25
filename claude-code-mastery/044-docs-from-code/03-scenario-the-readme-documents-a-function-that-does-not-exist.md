---
type: scenario
title: "Scenario: the README documents a function that does not exist"
minutes: 11
---

A generated README for the `textstats` package is merged. A week later a user files an issue: "`sentence_count(text)` from the README raises AttributeError." Nobody wrote that function; the model added it because text-stats libraries usually have one.

### Q1. Which check would have caught this before merge?

- A. A spell checker
- B. Comparing every documented signature with the module's real functions
- C. Reading the README carefully
- D. A longer prompt

<details><summary>Answer</summary>

**Answer: B** - An ast comparison fails on any documented name the module doesn't define.

</details>

### Q2. The README's example `>>> top_words("b a b")` shows `['a', 'b']` but the code returns `['b', 'a']`. Which check fails?

- A. doctest, because the printed output differs
- B. The signature check
- C. None
- D. The coverage check

<details><summary>Answer</summary>

**Answer: A** - doctest compares real output with what the README claims.

</details>

### Q3. How do you stop this class of bug from coming back when the code changes later?

- A. Run the verifier in CI so a stale README fails the build
- B. Regenerate the README monthly
- C. Freeze the code
- D. Remove examples

<details><summary>Answer</summary>

**Answer: A** - A check that runs on every change keeps the docs honest.

</details>

### Q4. Why tell Claude to run the verifier inside the same job?

- A. It is faster to type
- B. It iterates against a real check instead of stopping when the README looks right
- C. Claude can't write files otherwise
- D. doctest needs it

<details><summary>Answer</summary>

**Answer: B** - The agent loop works best with an objective stop condition.

</details>
