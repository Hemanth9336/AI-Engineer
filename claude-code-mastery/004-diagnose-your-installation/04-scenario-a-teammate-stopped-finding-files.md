---
type: scenario
title: "Scenario: a teammate stopped finding files"
minutes: 8
---

A teammate says that since yesterday Claude Code cannot find any files: `@` mentions show nothing, their custom agents do not load, and searches come back empty. They recently set `USE_BUILTIN_RIPGREP=0` because a blog post said the system ripgrep is faster. Their machine has no `rg` installed.

### Q1. What is the quickest way to confirm the cause?

- A. Reinstall Claude Code
- B. Delete ~/.claude
- C. Run claude doctor and read the Search line
- D. Switch to a bigger model

<details><summary>Answer</summary>

**Answer: C** - The Search line shows whether the bundled or a system ripgrep is in use and whether it works.

</details>

### Q2. What fixes it?

- A. Turn on auto-compaction
- B. Install the ripgrep package (or unset USE_BUILTIN_RIPGREP) so a working ripgrep is available
- C. Add Read to the allow list
- D. Use plan mode

<details><summary>Answer</summary>

**Answer: B** - Search, @file mentions, custom agents and skills all depend on ripgrep; telling Claude Code to use a system copy that does not exist breaks them.

</details>

### Q3. How would a baseline from last week have helped?

- A. It would not - baselines only record the version
- B. It would have blocked the environment variable
- C. diff would show the search line changed from OK (bundled), pointing straight at the cause
- D. It would have reinstalled ripgrep automatically

<details><summary>Answer</summary>

**Answer: C** - Comparing today's baseline with a known-good one shows exactly which fact changed.

</details>
