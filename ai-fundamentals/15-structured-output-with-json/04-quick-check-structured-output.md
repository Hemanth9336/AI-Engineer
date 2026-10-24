---
type: quiz
title: "Quick check: structured output"
minutes: 6
---

### Q1. You turn on JSON mode but don't describe any keys. What happens?

- A. The model returns your schema automatically
- B. The request always fails
- C. You get valid JSON, but the keys and shape are up to the model
- D. The model returns plain text

<details><summary>Answer</summary>

**Answer: C** - JSON mode guarantees syntax only. The schema comes from your prompt or a json_schema.

</details>

### Q2. The model returns {"port": "5432"}. Why might that break your program?

- A. It is invalid JSON
- B. It is too long
- C. The key should be uppercase
- D. The port is a string, not a number, so numeric comparisons fail

<details><summary>Answer</summary>

**Answer: D** - Valid JSON can still have the wrong types. Specify types and validate them.

</details>

### Q3. What is the safest way to use a model's JSON in a script?

- A. Trust it - JSON mode was on
- B. Parse it, check required keys, types, and allowed values, and retry or fail if it doesn't match
- C. Use eval on it
- D. Paste it into a shell command

<details><summary>Answer</summary>

**Answer: B** - Treat model output as untrusted input: parse and validate before use.

</details>

### Q4. A field may be missing from the input text. How do you stop the model inventing a value?

- A. Raise the temperature
- B. Remove that key
- C. Tell it to use null when the text doesn't say
- D. Use a bigger max_tokens

<details><summary>Answer</summary>

**Answer: C** - An explicit 'unknown' option removes the pressure to guess.

</details>
