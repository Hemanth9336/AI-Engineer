---
type: scenario
title: "Scenario: the agent proposes an upload"
minutes: 11
---

A teammate asks Claude to "share the failing config with the vendor". Claude proposes `tar czf - config/ | curl -T - https://files.vendor.example/upload`. `config/` holds `prod.env`. Your project has the exfiltration guard from this topic.

### Q1. Does the guard catch this command?

- A. It depends on the pattern: `config/` is not a secret source, so it slips through unless you add it or block uploads of whole directories
- B. No - it never mentions .env as a word
- C. Yes, always
- D. Only in plan mode

<details><summary>Answer</summary>

**Answer: A** - Pattern guards only catch what they list - review the list against your real secret locations.

</details>

### Q2. You extend the guard to deny `curl -T` and `--data-binary @` uploads entirely. A week later the release job that uploads build artifacts breaks. Best fix?

- A. Allow-list the release destination host in the hook while keeping uploads elsewhere denied
- B. Remove the guard
- C. Disable all hooks in CI
- D. Make the hook exit 1

<details><summary>Answer</summary>

**Answer: A** - Guards need explicit, reviewed exceptions - not removal.

</details>

### Q3. Claude, denied, tries `python3 -c 'import urllib.request; ...'` instead. What does that tell you?

- A. Pattern guards are a speed bump: back them with network isolation (sandbox allowed domains) for real protection
- B. The hook is broken
- C. Python is always safe
- D. Nothing

<details><summary>Answer</summary>

**Answer: A** - Any language can open a socket; only network-level controls make exfiltration impossible.

</details>

### Q4. What should the deny reason say?

- A. Nothing
- B. A stack trace
- C. Why it was blocked and what to do instead, e.g. describe the config difference without sending files
- D. The secret's value

<details><summary>Answer</summary>

**Answer: C** - Claude acts on the reason - make it a usable instruction.

</details>
