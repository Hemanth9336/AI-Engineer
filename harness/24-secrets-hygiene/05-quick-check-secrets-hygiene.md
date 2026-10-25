---
type: quiz
title: "Quick check: secrets hygiene"
minutes: 3
---

### Q1. A tool needs an API token. Where should the token come from?

- A. The system prompt
- B. The tool's code reads it from the environment - the model never sees it
- C. The user types it in chat
- D. A tool argument the model fills in

<details><summary>Answer</summary>

**Answer: B** - Authentication happens outside the model.

</details>

### Q2. Why test for leaks with a fake key?

- A. Fake keys are faster
- B. If the fake key shows up in a file or request, the real key would too - and the fake one unlocks nothing
- C. Real keys can't be logged
- D. The provider requires it

<details><summary>Answer</summary>

**Answer: B** - Plant a fake, search for it.

</details>

### Q3. Which is a leak even if no file contains the key?

- A. The key in an environment variable
- B. The key length in a log
- C. The key in a secret manager
- D. The key in the system prompt - it's sent to the provider and shows up in traces

<details><summary>Answer</summary>

**Answer: D** - Putting a key in context sends it everywhere the context goes.

</details>

### Q4. Where should redaction happen?

- A. In each log call separately
- B. Only in production
- C. In one function every log line passes through, on the final serialized text
- D. In the model

<details><summary>Answer</summary>

**Answer: C** - One choke point means a new log line can't forget it.

</details>

### Q5. A crash handler writes dict(os.environ) to a file. What's wrong?

- A. Nothing
- B. It needs JSON
- C. It's too long
- D. The environment holds the API key and other secrets - log the error, not the environment

<details><summary>Answer</summary>

**Answer: D** - Environment dumps are one of the most common key leaks.

</details>
