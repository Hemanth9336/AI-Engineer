---
type: quiz
title: "Quick check: where a shared rule lives"
minutes: 6
---

### Q1. Your repo has `AGENTS.md` with all team rules. A teammate adds a two-line `CLAUDE.md` with a Claude-only tip. What happens in Claude Code by default?

- A. Claude reads both files
- B. Claude reads only CLAUDE.md and loses the AGENTS.md rules
- C. Claude reads only AGENTS.md
- D. Claude refuses to start

<details><summary>Answer</summary>

**Answer: B** - By default Claude reads AGENTS.md only when no CLAUDE.md exists on the path. Add @AGENTS.md to the CLAUDE.md.

</details>

### Q2. Which layout keeps one copy of the shared rules for both Claude Code and Codex?

- A. Rules in CLAUDE.md, AGENTS.md containing @CLAUDE.md
- B. Rules in .claude/settings.json
- C. The same rules pasted into both files
- D. Rules in AGENTS.md, CLAUDE.md containing @AGENTS.md

<details><summary>Answer</summary>

**Answer: D** - Codex has no import syntax, so the canonical text goes in AGENTS.md and Claude imports it.

</details>

### Q3. Where does a Codex user put personal, uncommitted instructions for one directory that win over the team's `AGENTS.md` there?

- A. CLAUDE.local.md
- B. ~/.codex/config.toml
- C. AGENTS.override.md in that directory
- D. A comment at the top of AGENTS.md

<details><summary>Answer</summary>

**Answer: C** - Codex checks AGENTS.override.md before AGENTS.md in each directory and uses at most one file per directory.

</details>

### Q4. Your combined Codex instructions are 50 KiB. What happens with default settings?

- A. Codex refuses to start
- B. Codex summarizes the files
- C. Codex stops adding files at project_doc_max_bytes (32 KiB)
- D. Nothing - there is no limit

<details><summary>Answer</summary>

**Answer: C** - Raise project_doc_max_bytes or split the guidance into nested directories.

</details>
