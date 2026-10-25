---
type: quiz
title: "Quick check: who wins the conflict"
minutes: 9
---

### Q1. Managed settings deny `WebFetch`. A developer passes `--allowedTools WebFetch`. What happens?

- A. The flag wins
- B. Only in -p mode
- C. Claude asks
- D. WebFetch stays denied - managed settings are above the command line

<details><summary>Answer</summary>

**Answer: D** - Nothing a developer controls overrides a managed value.

</details>

### Q2. Server-managed settings and a managed-settings.json file both deliver policy to a laptop. By default which applies?

- A. They merge
- B. Whichever is newer
- C. The file
- D. Only the server-managed settings - the highest-ranked source with a policy wins, the rest are ignored

<details><summary>Answer</summary>

**Answer: D** - first-wins is the default; managedSourcesBehavior: merge changes it.

</details>

### Q3. Managed `availableModels` is `["sonnet", "haiku"]`. A developer runs `/model opus`. Result?

- A. It switches
- B. It uses haiku silently
- C. It switches for one turn
- D. It's refused - opus isn't on the allowlist

<details><summary>Answer</summary>

**Answer: D** - availableModels restricts every way of selecting a model.

</details>

### Q4. Project settings allow `Bash(npm publish*)`; managed settings set `allowManagedPermissionRulesOnly: true` with no such rule. Can the agent publish without asking?

- A. Yes
- B. Only the repo owner
- C. Only in acceptEdits mode
- D. No - only managed permission rules count, so the project's allow is ignored

<details><summary>Answer</summary>

**Answer: D** - The lock makes every non-managed allow, ask, and deny irrelevant.

</details>

### Q5. Can a developer add a stricter deny rule of their own on a managed machine?

- A. No, managed settings forbid any change
- B. Only in CLAUDE.md
- C. Only admins
- D. Yes - lower levels can't loosen managed policy, but deny rules still add up

<details><summary>Answer</summary>

**Answer: D** - Stricter values from lower levels still count; looser ones never do.

</details>
