---
type: quiz
title: "Quick check: what compaction keeps"
minutes: 9
---

### Q1. After compaction, which of these is re-injected from disk?

- A. A decision you made in conversation an hour ago
- B. The project-root CLAUDE.md
- C. Every file the agent ever read
- D. The full text of earlier tool results

<details><summary>Answer</summary>

**Answer: B** - Project-root CLAUDE.md and auto memory are reloaded; conversation details survive only through the summary.

</details>

### Q2. You are about to start a long new task in a session already full of debugging noise. Best move?

- A. Keep going - auto-compaction will handle it
- B. Run /context twice
- C. Switch to a bigger model
- D. /compact focus on the new task, or /clear and start fresh

<details><summary>Answer</summary>

**Answer: D** - Focused compaction or a fresh session gives the new task a clean window.

</details>

### Q3. Why write a handoff file from the session that did the work rather than from a new one?

- A. New sessions cannot write files
- B. The working session holds the context about what was done and why
- C. Handoffs require --continue
- D. It is cheaper

<details><summary>Answer</summary>

**Answer: B** - Only the working session knows the decisions; resuming it to write the handoff captures them.

</details>

### Q4. What does the --resume flag do in a headless run?

- A. Starts a new session with the same prompt
- B. Restores files to an earlier state
- C. Replays the old session's tool calls
- D. Continues the given session, with its history, under the same session id

<details><summary>Answer</summary>

**Answer: D** - --resume continues the conversation; the envelope's session_id stays the same.

</details>
