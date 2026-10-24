---
type: quiz
title: "Quick check: structured output"
minutes: 3
---

### Q1. What does JSON mode (`response_format: json_object`) guarantee?

- A. The right field names
- B. Correct values
- C. Syntactically valid JSON
- D. No hallucinations

<details><summary>Answer</summary>

**Answer: C** - Syntax only - shape still needs validation.

</details>

### Q2. The ticket has no order ID. How do you stop the model inventing one?

- A. Higher temperature
- B. Remove the field
- C. Tell it to use null when no order ID is mentioned, and validate the pattern
- D. Use a bigger model

<details><summary>Answer</summary>

**Answer: C** - Explicit missing-data instructions plus validation.

</details>

### Q3. Validation fails. What should the retry message contain?

- A. Nothing - just call again
- B. A threat
- C. The bad reply and the exact validation errors
- D. A higher max_tokens

<details><summary>Answer</summary>

**Answer: C** - Models correct well when told exactly what was wrong.

</details>

### Q4. Why pass `ask` into `extract_with_retry` instead of calling the API inside?

- A. It's faster
- B. The SDK requires it
- C. So the retry logic can be tested with fake replies, without a model
- D. To hide the key

<details><summary>Answer</summary>

**Answer: C** - Dependency injection makes the loop testable and repeatable.

</details>
