---
type: scenario
title: "Scenario: planning the next iteration"
minutes: 11
---

The release manager has run for a month on the pricing app. Three other teams want it. The usage log shows: the notes worker costs four times as much as everything else combined; the guard fired 31 times, 27 of them on `git push` from the fix-it runs; and two releases went out with notes that mentioned a change that wasn't in them.

### Q1. What do you fix first?

- A. Cost
- B. The guard noise
- C. The notes that described changes that weren't released - it's a correctness failure customers saw
- D. Onboarding the other teams

<details><summary>Answer</summary>

**Answer: C** - Wrong information shipped to customers outranks cost and convenience.

</details>

### Q2. How do you fix the hallucinated notes for good?

- A. Verify the draft with code: each bullet must map to a changelog entry, and fail the coordinator otherwise; add the bad cases to a test set
- B. Ask the worker to be careful
- C. Use a bigger model
- D. Drop the notes worker

<details><summary>Answer</summary>

**Answer: A** - Wrap the agent's output in a deterministic check, as with the verdict.

</details>

### Q3. 27 guard denials on git push. What does that tell you?

- A. The guard is broken
- B. The fix-it prompt or the agent's habits lead it to push; tell it plainly that publishing is human, and keep the guard as the backstop
- C. Remove the guard
- D. Allow pushes

<details><summary>Answer</summary>

**Answer: B** - A guard that fires often signals an instruction problem, not a guard problem.

</details>

### Q4. How do you offer it to three more teams without three forks?

- A. Copy the folder three times
- B. Move repo-specific bits (test command, version file, ports) into config, and package the agents, hooks, and commands as a plugin
- C. Tell them to rewrite it
- D. Run it centrally for everyone with no config

<details><summary>Answer</summary>

**Answer: B** - Configuration plus a plugin (topic 041) is how Claude Code tooling is shared.

</details>

### Q5. The notes worker is expensive. What's the cheapest effective change?

- A. Remove it
- B. Cache everything forever
- C. Run it on a smaller model with --model, keep the deterministic verification, and measure that quality holds on your saved cases
- D. Run it twice and pick one

<details><summary>Answer</summary>

**Answer: C** - Model choice is a measured decision (topic 063): smaller model, same checks, same test set.

</details>
