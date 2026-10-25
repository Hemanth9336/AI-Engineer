---
type: quiz
title: "Quick check: where the file contents go"
minutes: 11
---

### Q1. The secrets auditor reads `app/config.py`. Where do the file's contents live afterwards?

- A. In the main context
- B. In the subagent's own transcript and context; the main context gets only the auditor's final reply
- C. Nowhere
- D. In CLAUDE.md

<details><summary>Answer</summary>

**Answer: B** - That isolation is the point of delegating reads.

</details>

### Q2. Why make the auditors reply with JSON only?

- A. Models prefer JSON
- B. It's required by --agents
- C. Subagents can't write prose
- D. The reply is all the parent receives; small structured output is cheap to carry and easy to merge with code

<details><summary>Answer</summary>

**Answer: D** - The parent pays for every token of every reply.

</details>

### Q3. An auditor has `tools: Read, Grep, Glob`. It decides to fix the secret it found. What happens?

- A. It can't: Edit and Write aren't in its tool list
- B. It edits the file
- C. It asks the parent
- D. It runs sed through Bash

<details><summary>Answer</summary>

**Answer: A** - The tools allowlist is enforced; Bash isn't available either.

</details>

### Q4. How do you prove the main conversation never read a file?

- A. Ask Claude
- B. Check git log
- C. Search the main transcript for a sentinel from the file, and find it only in a subagents/ transcript
- D. Count tokens

<details><summary>Answer</summary>

**Answer: C** - Transcripts are the ground truth for what each context saw.

</details>
