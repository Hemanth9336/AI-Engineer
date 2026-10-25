---
type: quiz
title: "Quick check: where the status line text comes from"
minutes: 6
---

### Q1. Where does the text in the status line come from?

- A. Claude writes it each turn
- B. The stdout of the command in statusLine, fed session JSON on stdin
- C. A fixed template in Claude Code
- D. The last line of CLAUDE.md

<details><summary>Answer</summary>

**Answer: B** - Claude Code runs your command and displays whatever it prints.

</details>

### Q2. Your status line shows `ctx null%` right after startup. Why?

- A. The script is broken for all inputs
- B. used_percentage is null before the first reply; default it with // 0
- C. Context tracking is disabled
- D. jq is missing

<details><summary>Answer</summary>

**Answer: B** - Some fields are absent or null early in a session, so scripts must default them.

</details>

### Q3. You bound `j` (no modifier) to an action in the Chat context and now cannot type the letter j. What should you use?

- A. The Global context
- B. A ctrl+ or meta+ chord
- C. A longer key name
- D. vimInsertModeRemaps

<details><summary>Answer</summary>

**Answer: B** - Bare letters in the prompt are typing; bind chords instead.

</details>

### Q4. A repository's .claude/settings.json sets vimInsertModeRemaps. What happens?

- A. It applies to everyone
- B. It overrides your user setting
- C. It is ignored - remaps are user or managed scope only
- D. Claude Code errors

<details><summary>Answer</summary>

**Answer: C** - A repository cannot remap your keystrokes.

</details>
