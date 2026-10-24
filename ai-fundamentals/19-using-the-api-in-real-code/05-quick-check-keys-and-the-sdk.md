---
type: quiz
title: "Quick check: keys and the SDK"
minutes: 5
---

### Q1. Your script calls OpenAI() with no arguments. Where do the URL and key come from?

- A. OPENAI_BASE_URL and OPENAI_API_KEY in the environment
- B. They are built into the SDK
- C. A file called key.txt
- D. The model provides them

<details><summary>Answer</summary>

**Answer: A** - The SDK reads them from the environment, keeping secrets out of code.

</details>

### Q2. Which call is valid for the Anthropic Messages API?

- A. messages.create(model=..., messages=[...]) with no max_tokens
- B. messages.create(model=..., max_tokens=300, system="...", messages=[...])
- C. chat.completions.create(model=..., messages=[...])
- D. messages.create(prompt="...")

<details><summary>Answer</summary>

**Answer: B** - max_tokens is required, and system is a separate parameter.

</details>

### Q3. A key was committed to git yesterday. What fixes it?

- A. Deleting the file
- B. Rotating the key at the provider, then removing it from the code
- C. Force-pushing over the commit only
- D. Encrypting the repo

<details><summary>Answer</summary>

**Answer: B** - Treat a committed key as leaked: revoke it first.

</details>

### Q4. Why print token usage to stderr instead of stdout in a CLI?

- A. stderr is faster
- B. stdout can't print numbers
- C. So `tool > answer.txt` or a pipe gets only the answer
- D. The SDK requires it

<details><summary>Answer</summary>

**Answer: C** - Keep the useful output clean; diagnostics go to stderr.

</details>
