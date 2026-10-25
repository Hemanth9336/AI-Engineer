---
type: scenario
title: "Log full prompts for debugging"
minutes: 3
---

**Situation.** Stackline's agent sometimes gives strange answers, and the team can't reproduce them. A senior engineer proposes: "Log every full request and response - all messages, all tool results, all headers - to our central logging service, kept for a year. Then we can replay anything."

The agent reads customer tickets and account data, and some tools return internal config. The central logging service is readable by about 200 engineers and is shipped to a third-party vendor.

### Q1. What's the biggest problem with the proposal as written?

- A. Logs are expensive
- B. Logging slows the agent down
- C. Headers contain API keys, and tool results contain customer data and internal config - now readable by 200 people and a vendor for a year
- D. Replays are impossible

<details><summary>Answer</summary>

**Answer: C** - Full transcripts are valuable and sensitive. Where they go and who can read them matters as much as having them.

</details>

### Q2. Which version keeps the debugging value?

- A. Log nothing
- B. Log everything but encrypt the disk
- C. Log only the final answers
- D. Log full transcripts without headers, through redaction, to a restricted store with a short retention, plus metadata (models, tokens, tool names) in the central log

<details><summary>Answer</summary>

**Answer: D** - Split sensitive transcripts from shareable metadata.

</details>

### Q3. A tool result contains a customer's full address. What should redaction do?

- A. Nothing - it's not a key
- B. Follow the data policy: mask personal data in shared logs, and keep the unmasked transcript only where access is controlled
- C. Delete the transcript
- D. Ask the model to remove it

<details><summary>Answer</summary>

**Answer: B** - Secrets aren't only keys. Personal data has its own rules.

</details>

### Q4. How do you check that the redaction actually works?

- A. Trust the regex
- B. Run the agent with fake keys and seeded fake personal data, then search the logs for them - in CI
- C. Read a few log lines
- D. Ask the vendor

<details><summary>Answer</summary>

**Answer: B** - A leak test with planted fakes, run automatically, catches regressions.

</details>

### Q5. Six months later someone adds a new tool that returns a database URL with a password. What protects you?

- A. The leak test with planted fakes runs on every change, and redaction covers secret-shaped values by default
- B. Nothing
- C. The model hides it
- D. The vendor deletes it

<details><summary>Answer</summary>

**Answer: A** - Redaction and leak tests have to be part of the harness, not a one-off cleanup.

</details>
