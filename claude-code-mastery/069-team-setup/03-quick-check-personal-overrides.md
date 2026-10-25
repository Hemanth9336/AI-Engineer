---
type: quiz
title: "Quick check: personal overrides"
minutes: 11
---

### Q1. You want `Bash(open *)` allowed for yourself only, in this repo. Where does it go?

- A. .claude/settings.json
- B. ~/.claude/settings.json
- C. CLAUDE.md
- D. .claude/settings.local.json (gitignored)

<details><summary>Answer</summary>

**Answer: D** - Local project settings are personal and per repo; the user file would apply to every project.

</details>

### Q2. The team's `.claude/settings.json` denies `Bash(git push*)`. Your `settings.local.json` allows `Bash(git push origin main)`. What happens?

- A. Your allow wins; local is higher
- B. It depends on the model
- C. Claude asks
- D. The push is denied - deny rules from any level are checked before allows

<details><summary>Answer</summary>

**Answer: D** - Permission rules merge across levels and deny is evaluated first.

</details>

### Q3. A teammate's agent doesn't know the ticket prefix, but yours does. Most likely cause?

- A. The convention is in your CLAUDE.local.md or ~/.claude/CLAUDE.md instead of a committed file
- B. Different models
- C. Their cache
- D. They need /init

<details><summary>Answer</summary>

**Answer: A** - Test from a fresh clone with an empty HOME to catch configuration that only exists on your machine.

</details>

### Q4. Where should "I prefer terse answers" go?

- A. CLAUDE.md
- B. .claude/settings.json
- C. CLAUDE.local.md or ~/.claude/CLAUDE.md
- D. docs/conventions.md

<details><summary>Answer</summary>

**Answer: C** - Preferences are personal; they add to the team's instructions without changing them for anyone else.

</details>

### Q5. You set `model` in `.claude/settings.json` and a teammate sets a different `model` in their `settings.local.json`. Which applies to them?

- A. The team's
- B. Neither
- C. Theirs - for scalar settings the higher level (local) wins
- D. The default

<details><summary>Answer</summary>

**Answer: C** - Scalars take the highest level that sets them; only managed settings can't be overridden.

</details>
