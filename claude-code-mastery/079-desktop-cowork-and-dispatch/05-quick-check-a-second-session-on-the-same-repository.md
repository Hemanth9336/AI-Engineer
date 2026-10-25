---
type: quiz
title: "Quick check: a second session on the same repository"
minutes: 9
---

### Q1. You open a second Code session on the same repo while the first is editing. What prevents conflicts?

- A. Nothing; it's fine
- B. Turning on the Worktree toggle so each session gets its own git worktree and branch
- C. Plan mode
- D. A different model

<details><summary>Answer</summary>

**Answer: B** - Without worktrees both sessions edit the same files.

</details>

### Q2. Where are Desktop's worktrees created by default?

- A. <project-root>/.claude/worktrees/
- B. /tmp
- C. ~/worktrees
- D. In the cloud

<details><summary>Answer</summary>

**Answer: A** - Configurable in Settings > Claude Code.

</details>

### Q3. The new worktree session fails because `.env.local` is missing (it's gitignored). Fix?

- A. Commit .env.local
- B. List it in .worktreeinclude so it's copied into new worktrees
- C. Disable worktrees
- D. Paste it into the prompt

<details><summary>Answer</summary>

**Answer: B** - .worktreeinclude copies chosen gitignored files.

</details>

### Q4. You pick Accept edits for a folder in Desktop. Your settings say defaultMode: plan. Which applies next time in that folder?

- A. plan
- B. Auto
- C. Manual
- D. Accept edits - a selector pick is remembered per folder and outranks defaultMode (Plan picks are the exception)

<details><summary>Answer</summary>

**Answer: D** - Per-folder memory beats the default.

</details>

### Q5. A skill works in Cowork but not in your terminal session. Where is it configured?

- A. ~/.claude/skills
- B. In your claude.ai account's Customize settings - check you're signed in to the same account in the terminal
- C. .claude/settings.json
- D. claude_desktop_config.json

<details><summary>Answer</summary>

**Answer: B** - Cowork's skills come from account-synced configuration.

</details>
