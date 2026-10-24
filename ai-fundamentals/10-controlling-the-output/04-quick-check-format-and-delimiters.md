---
type: quiz
title: "Quick check: format and delimiters"
minutes: 6
---

### Q1. A script splits the reply on new lines and expects only checklist items, but the first line is 'Here is your checklist:'. What prompt change fixes it?

- A. Ask for a longer checklist
- B. Say 'Output only the checklist lines - no heading, introduction, or closing line'
- C. Remove the system message
- D. Raise the temperature

<details><summary>Answer</summary>

**Answer: B** - Models add polite framing unless told not to. Rule it out explicitly.

</details>

### Q2. Why wrap a customer email in <email> tags inside your prompt?

- A. They mark exactly where the data starts and ends, so it is not confused with your instructions
- B. Tags make the request cheaper
- C. The API requires XML
- D. Tags encrypt the email

<details><summary>Answer</summary>

**Answer: A** - Delimiters separate instructions from data, and let you refer to the data by name.

</details>

### Q3. Which is the safest way to put a file's contents into a JSON request from the shell?

- A. Use jq --arg to insert it, so quotes and newlines are escaped correctly
- B. Paste it into the JSON by hand
- C. Use echo inside single quotes
- D. Send the file name and let the model open it

<details><summary>Answer</summary>

**Answer: A** - `jq --arg` escapes the text properly. Hand-written JSON breaks on quotes and newlines.

</details>

### Q4. Your prompt asks for '4 to 6 items'. How should your code treat a reply with 9 items?

- A. Use it anyway
- B. Assume the model knows best
- C. Delete the extra items silently and continue
- D. Detect it with a format check, then retry or flag it

<details><summary>Answer</summary>

**Answer: D** - Prompts reduce format errors; checks catch the rest. Never assume the shape.

</details>
