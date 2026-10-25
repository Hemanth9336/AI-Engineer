---
type: scenario
title: "Scenario: the code is almost right"
minutes: 4
---

You asked Claude to add CSV export to a reporting tool. It worked: the file downloads and has the right columns. But dates come out as `2026-10-20T00:00:00` instead of `20/10/2026`, and the export also quietly renamed a helper function that two other modules import.

### Q1. What do you do next?

- A. Ask "can you make it better?"
- B. Throw the work away with /clear and ask for the whole feature again
- C. Fix the dates yourself and leave the rename
- D. Tell it exactly what's wrong in the same session: dates as DD/MM/YYYY, and restore the helper's original name

<details><summary>Answer</summary>

**Answer: D** - Most of it is right. Specific feedback in the same session keeps what works.

</details>

### Q2. How do you stop the surprise rename from happening again on the next task?

- A. Say what not to do in the brief - "don't rename or refactor anything outside the export" - and add it to CLAUDE.md if it keeps happening
- B. Switch to a bigger model
- C. Never let Claude edit more than one file
- D. Use bypassPermissions

<details><summary>Answer</summary>

**Answer: A** - Constraints in the brief, and recurring ones in project memory.

</details>

### Q3. Before you accept the fixed version, what's the best check?

- A. Run the test suite and read `git diff`, then add a test for the date format
- B. Trust Claude's summary
- C. Check the file downloads once
- D. Ask Claude if it's sure

<details><summary>Answer</summary>

**Answer: A** - Verify with tests and the diff - and pin the fixed behavior with a test.

</details>
