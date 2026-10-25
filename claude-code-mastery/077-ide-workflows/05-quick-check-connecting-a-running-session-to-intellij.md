---
type: quiz
title: "Quick check: connecting a running session to IntelliJ"
minutes: 9
---

### Q1. You started `claude` in an external terminal and want IntelliJ's diff viewer. What do you run?

- A. /mcp
- B. claude --ide
- C. /ide - from the same project root as the IDE
- D. /config

<details><summary>Answer</summary>

**Answer: C** - /ide connects a running CLI session to the IDE; start in the project root so the files match.

</details>

### Q2. The plugin says it cannot launch Claude Code. Most likely cause?

- A. The claude CLI isn't installed or isn't on the plugin's Claude command path - the JetBrains plugin doesn't bundle it
- B. The IDE is outdated
- C. No license
- D. Wrong theme

<details><summary>Answer</summary>

**Answer: A** - Install the CLI and set the Claude command path if needed.

</details>

### Q3. After an edit, Claude doesn't mention the new compile error IntelliJ shows. Why?

- A. It ignored it
- B. It needs VS Code
- C. Diagnostics are disabled
- D. In JetBrains, Claude doesn't fetch diagnostics on its own after edits; ask it to (getDiagnostics)

<details><summary>Answer</summary>

**Answer: D** - Make checking diagnostics part of the instructions.

</details>

### Q4. You use JetBrains Remote Development. Where does the plugin go?

- A. On your laptop
- B. Both
- C. On the remote host (Settings > Plugin (Host))
- D. Nowhere

<details><summary>Answer</summary>

**Answer: C** - The plugin must run where the project and the CLI run.

</details>

### Q5. A teammate enables Accept connections from all network interfaces. What's the risk?

- A. None
- B. It disables diagnostics
- C. Slower diffs
- D. The unencrypted ws:// session traffic and its token cross the local network in cleartext

<details><summary>Answer</summary>

**Answer: D** - Keep it on loopback unless there's no alternative, and prefer WSL mirrored networking.

</details>
