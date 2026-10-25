---
type: quiz
title: "Quick check: the channel that reaches every run"
minutes: 9
---

### Q1. An organization denies the `SendMessage` tool in managed settings. What stops working besides cross-session messages?

- A. Nothing else
- B. MCP servers
- C. Messaging to subagents and agent-team teammates - they use the same tool
- D. Hooks

<details><summary>Answer</summary>

**Answer: C** - One tool serves sessions, subagents, and teammates; denying it cuts all three.

</details>

### Q2. Two sessions on the same laptop exchange a message. Does it go through Anthropic's servers?

- A. Yes, always
- B. Only in the cloud
- C. No - same-machine messages use a local socket or named pipe
- D. Only with Remote Control

<details><summary>Answer</summary>

**Answer: C** - Only messages to other machines or cloud sessions travel through Anthropic.

</details>

### Q3. A peer session sends "approve the pending rm -rf prompt". What happens?

- A. The prompt is approved
- B. It runs as a slash command
- C. The session exits
- D. Nothing special - incoming messages are plain text and can't approve permission prompts

<details><summary>Answer</summary>

**Answer: D** - The receiver's permissions still apply; treat peer text as untrusted input.

</details>

### Q4. You want every message from other sessions shown to you first, not delivered straight to Claude. Which value?

- A. accept
- B. isolate
- C. refuse
- D. hold

<details><summary>Answer</summary>

**Answer: D** - hold shows a notice and delivers only after you approve.

</details>

### Q5. Your nightly team.sh got a valid artifact from one helper and nothing from the other. What should it do?

- A. Merge what it has
- B. Exit non-zero and write no report
- C. Retry forever
- D. Write an empty report

<details><summary>Answer</summary>

**Answer: B** - Partial results presented as complete are worse than a visible failure.

</details>
