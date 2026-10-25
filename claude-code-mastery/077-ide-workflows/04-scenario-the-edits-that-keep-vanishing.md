---
type: scenario
title: "Scenario: the edits that keep vanishing"
minutes: 9
---

A developer says Claude's edits "keep vanishing" in VS Code. Claude reports success, the diff looked right, and then the change is gone. They turned `autosave` off last week because "it kept saving my half-finished code". They often have the same file open with unsaved changes.

### Q1. What's most likely happening?

- A. A Claude bug
- B. The extension is outdated
- C. Git hooks revert it
- D. Claude writes the file on disk, then the developer saves their stale unsaved buffer over it

<details><summary>Answer</summary>

**Answer: D** - With autosave off, the editor buffer and the file on disk diverge, and the last save wins.

</details>

### Q2. What's the fix that keeps their workflow sane?

- A. Turn autosave back on (files are saved before Claude reads or writes them), and avoid editing the same file while Claude does
- B. Stop using Claude
- C. Use bypass mode
- D. Disable checkpoints

<details><summary>Answer</summary>

**Answer: A** - autosave exists to keep Claude and the editor looking at the same contents.

</details>

### Q3. They also want Claude to stop seeing their selection in secrets.yaml. How?

- A. Close the file
- B. Turn off attachOpenFile only
- C. A Read deny rule for that path - it blocks selections and open-file context too
- D. Add it to the prompt

<details><summary>Answer</summary>

**Answer: C** - Read deny rules cover the selection and open-file notices.

</details>

### Q4. How do they check Claude's edit compiles without leaving the chat?

- A. Run the build by hand
- B. Reload the window
- C. Ask Claude to check diagnostics - mcp__ide__getDiagnostics reads the Problems panel
- D. Use plan mode

<details><summary>Answer</summary>

**Answer: C** - Diagnostics from the IDE are the quickest feedback loop.

</details>
