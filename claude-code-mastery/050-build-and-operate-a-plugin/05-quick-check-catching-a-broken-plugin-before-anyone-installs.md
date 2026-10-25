---
type: quiz
title: "Quick check: catching a broken plugin before anyone installs it"
minutes: 6
---

### Q1. `plugin.json` sets `"commands": "commands/deploy.md"`. What does `claude plugin validate` say?

- A. It fails: component paths must start with ./
- B. Nothing; relative paths are fine
- C. It warns that commands are deprecated
- D. It rewrites the path

<details><summary>Answer</summary>

**Answer: A** - Every component path is relative to the plugin root and must start with `./`.

</details>

### Q2. A teammate typed `"descripton"` in plugin.json. The plugin loads fine. How do you make CI catch it?

- A. It can't be caught
- B. claude plugin validate --strict, which turns the unknown-key warning into a failure
- C. claude plugin list
- D. /reload-plugins

<details><summary>Answer</summary>

**Answer: B** - Unknown keys are ignored at runtime and reported as warnings; --strict makes warnings fail the run.

</details>

### Q3. A shell-form hook command is `notify.sh --token ${user_config.api_token}`. What happens?

- A. It works
- B. The token is masked
- C. The hook fails with an error: shell-form commands reject ${user_config.*}; read CLAUDE_PLUGIN_OPTION_API_TOKEN instead
- D. Only sensitive values are rejected

<details><summary>Answer</summary>

**Answer: C** - A shell would re-parse the substituted value, so Claude Code refuses it; use exec form args or the environment variable.

</details>

### Q4. Where should a plugin keep a downloaded dependency cache so it survives updates?

- A. ${CLAUDE_PLUGIN_ROOT}/cache
- B. ${CLAUDE_PLUGIN_DATA}
- C. /tmp
- D. The project root

<details><summary>Answer</summary>

**Answer: B** - The plugin root is replaced on every update; the data directory persists until the last uninstall.

</details>

### Q5. A script runs `claude plugin disable team-kit` and the plugin is already disabled. What does it get?

- A. Exit 0
- B. Exit 1, and with --json failureCode already_in_goal_state with alreadyInGoalState true
- C. Exit 2
- D. A prompt

<details><summary>Answer</summary>

**Answer: B** - Read the JSON so 'already in the state I wanted' isn't treated as a real failure.

</details>
