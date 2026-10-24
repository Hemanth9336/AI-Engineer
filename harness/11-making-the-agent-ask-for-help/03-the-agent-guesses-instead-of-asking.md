---
type: scenario
title: "The agent guesses instead of asking"
minutes: 4
---

**Situation.** Stackline's release agent prepares releases. A developer typed: "Bump the version and tag it." The agent read `VERSION` (2.3.0), decided on its own that this was a **major** release, wrote `3.0.0`, created the tag `v3.0.0` and pushed it. The release pipeline picked up the tag and published 3.0.0 to customers - a breaking-change signal for a release that only contained two bug fixes.

The agent has tools `read_file`, `write_file`, `git_tag` and `git_push`. It has no way to ask questions. Its system prompt says "Be autonomous and don't bother the user."

### Q1. What's the root cause?

- A. The request was ambiguous (major, minor or patch?) and the harness gave the agent no way to ask - and told it not to
- B. The model can't count
- C. The VERSION file was wrong
- D. git push is too slow

<details><summary>Answer</summary>

**Answer: A** - Only the developer knew the release type. With no ask tool and a prompt discouraging questions, the model guessed.

</details>

### Q2. Which change fixes it best?

- A. Tell the model to think harder
- B. Hard-code patch releases
- C. Add an ask_user tool, describe when to use it (decisions only the user can make), and drop 'don't bother the user'
- D. Remove the git_push tool entirely

<details><summary>Answer</summary>

**Answer: C** - Give the model the ability to resolve ambiguity, and stop the prompt from forbidding it.

</details>

### Q3. The agent now asks 'Where is the VERSION file?' before every release. What should change?

- A. Nothing - more questions are safer
- B. Give it a bigger model
- C. Remove ask_user again
- D. The ask_user description: don't ask about things the other tools can find out

<details><summary>Answer</summary>

**Answer: D** - Over-asking is also a failure. The description should say what not to ask about - list_dir would find VERSION.

</details>

### Q4. The release agent also runs nightly in CI, where nobody can answer. What should ask_user do there?

- A. Wait for an answer until the job times out
- B. Pick the most common answer automatically
- C. Return 'error: the user is not available...' so the agent stops and reports what it needs
- D. Crash the job

<details><summary>Answer</summary>

**Answer: C** - An honest 'nobody is here' result turns a guess into a clear, actionable failure.

</details>

### Q5. Besides asking, what harness part should have stopped an unexpected 3.0.0 from reaching customers?

- A. A longer system prompt
- B. Higher temperature
- C. An approval gate before irreversible actions like pushing a release tag
- D. A larger context window

<details><summary>Answer</summary>

**Answer: C** - Pushing a tag that triggers a publish is irreversible. That's a confirmation gate - topic 15.

</details>
