---
type: scenario
title: "Scenario: stopping destructive git commands"
minutes: 9
---

An agent in your monorepo ran `git reset --hard` to "clean up" before a rebase and wiped an engineer's uncommitted work. You want a PreToolUse guard on Bash that stops history-destroying git commands while leaving normal git use alone.

### Q1. Which matcher and field does the guard inspect?

- A. Matcher Edit|Write, field file_path
- B. Matcher *, field cwd
- C. Matcher Bash, field tool_input.command
- D. Matcher git, field tool_name

<details><summary>Answer</summary>

**Answer: C** - Shell commands arrive as Bash calls; the command string is in tool_input.command.

</details>

### Q2. Your first draft blocks commands that **start with** `git reset --hard`. Claude runs `cd repo && git reset --hard HEAD~1`. What happens?

- A. It is blocked
- B. The hook times out
- C. Claude Code splits it for you
- D. It runs - the command does not start with git

<details><summary>Answer</summary>

**Answer: D** - Check every subcommand (split on &&, ;, |) or search the whole string - prefixes miss compound commands.

</details>

### Q3. The script crashes on a command with unusual quoting and exits 1. What happens to that command?

- A. It runs - exit 1 is non-blocking
- B. Blocked
- C. Claude is asked
- D. The session ends

<details><summary>Answer</summary>

**Answer: A** - Only exit 2 or a deny blocks. Add onFailure: block so a crash fails closed.

</details>

### Q4. Which list is a sensible block list that leaves daily work alone?

- A. git reset --hard, git clean -fd, git push --force, git branch -D, git checkout -- .
- B. Every git command
- C. git status and git diff
- D. git commit

<details><summary>Answer</summary>

**Answer: A** - Block what destroys history or uncommitted work; let status, diff, add, and commit through.

</details>

### Q5. Where else should the rule live?

- A. Nowhere - the hook is enough
- B. Also as deny rules such as Bash(git reset --hard*) and Bash(git push --force*) in settings, as a second layer
- C. Only in CLAUDE.md
- D. In .gitignore

<details><summary>Answer</summary>

**Answer: B** - Deny rules are simple and always win; the hook covers the patterns rules cannot express.

</details>
