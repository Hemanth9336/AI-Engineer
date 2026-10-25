---
type: quiz
title: "Quick check: prompt injection through tools"
minutes: 4
---

### Q1. What makes indirect prompt injection different from a user typing 'ignore your rules'?

- A. It's always harmless
- B. The instructions arrive inside content a tool reads, written by someone other than the user
- C. It only works on small models
- D. It needs access to the API key

<details><summary>Answer</summary>

**Answer: B** - The user is honest; the attacker wrote the ticket, page or file.

</details>

### Q2. Which three things together turn an injection into a breach?

- A. A long prompt, many tools, a big model
- B. Untrusted input, access to private data, and an outbound channel
- C. Python, JSON and HTTP
- D. A user, a model and a log

<details><summary>Answer</summary>

**Answer: B** - Remove any one and the attack can't complete.

</details>

### Q3. Why escape '</tool_result>' inside tool content?

- A. It saves tokens
- B. Otherwise the content can close your marker and write text that looks like it's outside the data block
- C. XML requires it
- D. To make it readable

<details><summary>Answer</summary>

**Answer: B** - An unescaped delimiter lets the attacker break out of the box you put them in.

</details>

### Q4. Which defense still works if the model fully obeys the injected text?

- A. A system prompt saying 'ignore injections'
- B. Least privilege: the tool can't read secrets and email can't leave the company
- C. A filter for 'ignore previous instructions'
- D. A bigger model

<details><summary>Answer</summary>

**Answer: B** - Controls enforced in code don't depend on the model's judgment.

</details>

### Q5. The harness blocked an email to an outside address requested by a tool result. What else should happen?

- A. Nothing
- B. Log it as a security event - someone planted that instruction
- C. Retry the email
- D. Delete the ticket silently

<details><summary>Answer</summary>

**Answer: B** - Blocked exfiltration attempts are evidence of an attack worth investigating.

</details>
