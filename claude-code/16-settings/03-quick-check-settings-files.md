---
type: quiz
title: "Quick check: settings files"
minutes: 4
---

### Q1. Where does a rule the whole team needs - deny reading `.env` - belong?

- A. `.claude/settings.json`, committed
- B. `.claude/settings.local.json`
- C. `~/.claude/settings.json`
- D. CLAUDE.md

<details><summary>Answer</summary>

**Answer: A** - Shared project settings travel with the repo.

</details>

### Q2. Where do you put "let Claude run git status without asking" just for yourself, in one repo?

- A. Managed settings
- B. `.claude/settings.json`
- C. `.claude/settings.local.json` (and keep it out of git)
- D. .mcp.json

<details><summary>Answer</summary>

**Answer: C** - Local project settings are personal.

</details>

### Q3. User settings allow `Bash(curl:*)`; managed settings deny it. What happens?

- A. curl is denied - deny wins, and managed policy can't be overridden
- B. curl is allowed
- C. Claude asks each time
- D. Claude Code refuses to start

<details><summary>Answer</summary>

**Answer: A** - Deny beats allow everywhere.

</details>

### Q4. Settings say `"model": "haiku"` but sessions use another model, and `ANTHROPIC_MODEL` is set. Why?

- A. You need to run /init
- B. Settings files are ignored
- C. haiku isn't a valid alias
- D. The environment variable outranks the settings file

<details><summary>Answer</summary>

**Answer: D** - /model > --model > ANTHROPIC_MODEL > settings.

</details>

### Q5. Which console command shows each permission rule and which file it came from?

- A. /context
- B. /model
- C. /clear
- D. /permissions

<details><summary>Answer</summary>

**Answer: D** - It's the place to debug rules.

</details>
