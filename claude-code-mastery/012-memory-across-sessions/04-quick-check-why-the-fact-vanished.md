---
type: quiz
title: "Quick check: why the fact vanished"
minutes: 9
---

### Q1. You told Claude the staging port during a long session, then started a new session tomorrow. It does not know the port. Most likely why?

- A. Nothing saved it to memory or CLAUDE.md - it only lived in the conversation
- B. The model forgot it overnight
- C. Auto memory only works with opus
- D. Sessions expire after 24 hours

<details><summary>Answer</summary>

**Answer: A** - Conversation content ends with the session unless a memory file or CLAUDE.md captured it.

</details>

### Q2. A teammate clones the repo and their Claude does not know a fact your Claude remembers. Why?

- A. Auto memory is machine-local and never committed
- B. They need --continue
- C. Their MEMORY.md is too long
- D. They use a different model

<details><summary>Answer</summary>

**Answer: A** - Auto memory lives under ~/.claude on your machine; shared knowledge belongs in CLAUDE.md.

</details>

### Q3. Your MEMORY.md has grown to 400 lines and old facts seem ignored. Why?

- A. Lines over 80 characters are skipped
- B. Memory expires after 30 days
- C. MEMORY.md is only read in plan mode
- D. Only the first 200 lines (or 25 KB) of MEMORY.md load at startup

<details><summary>Answer</summary>

**Answer: D** - Content past the startup limit is not loaded; keep the index to one line per memory.

</details>

### Q4. You typed `# use pnpm, not npm` in a current Claude Code build. What happened?

- A. It was sent as an ordinary prompt - current builds removed the # shortcut
- B. It was saved to CLAUDE.md
- C. It created a hook
- D. It was ignored entirely

<details><summary>Answer</summary>

**Answer: A** - The # shortcut is gone; ask Claude to remember it or add it with /memory.

</details>
