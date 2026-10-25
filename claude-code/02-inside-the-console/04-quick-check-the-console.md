---
type: quiz
title: "Quick check: the console"
minutes: 4
---

### Q1. You type `/clear` in the console. Who receives it?

- A. The console itself - slash commands are not sent to the model as a message
- B. The model, as a normal prompt
- C. Your shell
- D. Nobody - it's a comment

<details><summary>Answer</summary>

**Answer: A** - Slash commands are handled by Claude Code.

</details>

### Q2. Claude's first tool call is heading the wrong way. What's the cheapest fix?

- A. Type /init
- B. Let it finish, then undo everything
- C. Close the terminal
- D. Press Esc and tell it what you want instead

<details><summary>Answer</summary>

**Answer: D** - Interrupting early costs nothing and keeps the session.

</details>

### Q3. Why start `claude` inside the project folder rather than your home directory?

- A. It runs faster
- B. The working directory decides what it can see and edit, and which CLAUDE.md and settings load
- C. Sessions in home directories are not saved
- D. /model only works in projects

<details><summary>Answer</summary>

**Answer: B** - The folder scopes the session.

</details>

### Q4. Which command switches the current session to the small, fast model?

- A. /fast
- B. /model haiku
- C. claude --small
- D. /init haiku

<details><summary>Answer</summary>

**Answer: B** - `/model` switches; haiku is the quick one.

</details>

### Q5. You closed the terminal by accident. How do you pick up the same conversation?

- A. It's gone forever
- B. Run `claude -c` in the same folder
- C. Run `/init` again
- D. Copy the scrollback into a new session

<details><summary>Answer</summary>

**Answer: B** - Sessions are saved per folder; `-c` continues the latest.

</details>
