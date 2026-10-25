---
type: quiz
title: "Quick check: what teleport brings home"
minutes: 9
---

### Q1. What does `claude --teleport <id>` give you?

- A. The session's branch, fetched and checked out, plus its full conversation history
- B. Only the diff
- C. A read-only transcript
- D. A new cloud session

<details><summary>Answer</summary>

**Answer: A** - Branch plus conversation, in your terminal.

</details>

### Q2. After teleporting you keep working locally. Does the cloud session on claude.ai see your new messages?

- A. Yes
- B. After a push
- C. Only on mobile
- D. No - the terminal gets its own copy; start /remote-control to keep steering from other devices

<details><summary>Answer</summary>

**Answer: D** - Teleport is a copy, not a link.

</details>

### Q3. Teleport refuses to start. Your working tree has uncommitted edits. What's going on?

- A. Teleport needs a clean git state; stash or commit first
- B. A bug
- C. Wrong account
- D. The branch is too big

<details><summary>Answer</summary>

**Answer: A** - It checks out a branch over your tree.

</details>

### Q4. Can you push your current terminal session up to the cloud with --cloud?

- A. Yes
- B. No - from the CLI the handoff is one-way; --cloud starts a new session
- C. Only with -p
- D. Only from Desktop

<details><summary>Answer</summary>

**Answer: B** - Desktop's Open in can move a local Code-tab session; the CLI can't.

</details>

### Q5. Where should an API token the tests need go?

- A. A network secret, which the proxy attaches outside the VM
- B. Environment variables of the cloud environment
- C. The prompt
- D. The repo

<details><summary>Answer</summary>

**Answer: A** - Anyone using the environment can read its variables; network secrets never enter the VM.

</details>
