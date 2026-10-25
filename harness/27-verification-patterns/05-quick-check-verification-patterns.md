---
type: quiz
title: "Quick check: verification patterns"
minutes: 4
---

### Q1. Why run the verifier in a separate context from the generator?

- A. Without the generator's reasoning in view, it has nothing to defend and judges the claim against the evidence
- B. It's cheaper
- C. The API requires it
- D. So it can use tools

<details><summary>Answer</summary>

**Answer: A** - Same reason code review beats rereading your own code.

</details>

### Q2. The verifier replies 'Seems fine!' instead of JSON. What should the harness do?

- A. Treat it as pass
- B. Ask the user
- C. Crash
- D. Treat it as fail - a broken checker must not wave answers through

<details><summary>Answer</summary>

**Answer: D** - Fail closed.

</details>

### Q3. A summary claims '312 errors'. What's the strongest check?

- A. Ask a bigger model if it's right
- B. Check that the number looks plausible
- C. Ask the generator if it's sure
- D. Count the ERROR lines in the log with code

<details><summary>Answer</summary>

**Answer: D** - If it can be recomputed from the source, recompute it.

</details>

### Q4. How do you show a verifier actually catches errors?

- A. It passed all real outputs
- B. Read its code
- C. Plant a known error in each field and confirm it's caught - and that correct outputs still pass
- D. Run it once

<details><summary>Answer</summary>

**Answer: C** - Mutation testing for checkers.

</details>

### Q5. After 2 rejected retries, what should the harness return?

- A. The last answer as if it were fine
- B. The last answer, clearly marked as unverified
- C. Nothing
- D. A made-up correct answer

<details><summary>Answer</summary>

**Answer: B** - Be honest about what wasn't confirmed.

</details>
