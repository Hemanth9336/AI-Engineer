---
type: scenario
title: "Scenario: the self-approving pipeline"
minutes: 9
---

A team wires up CI so that when Claude opens a PR, a second Claude job reviews it with your checklist and, if the verdict is `approve`, auto-merges. Three weeks later a PR that "only renamed a variable" also removed an authorization check. It was approved and merged at 2am.

### Q1. What's the structural flaw?

- A. The checklist was too short
- B. The same kind of agent both wrote and approved the change, and no human was accountable for the merge
- C. The model was too small
- D. CI ran at night

<details><summary>Answer</summary>

**Answer: B** - An agent verdict is input to a human decision, not the decision itself.

</details>

### Q2. Which change keeps most of the speed but restores control?

- A. Let the agent review and label or comment, but require a human approval (branch protection) for every merge
- B. Remove the reviewer
- C. Use opus for the reviewer
- D. Run the review twice

<details><summary>Answer</summary>

**Answer: A** - Automation does the first pass; branch protection keeps people on the merge.

</details>

### Q3. The checklist had no rule for removed authorization checks. How do you stop the next one?

- A. Hope
- B. Lower the effort
- C. Ban renames
- D. Add an AUTHZ-REMOVED rule, add this PR's diff to your seeded set, and require recall on it before changing the reviewer

<details><summary>Answer</summary>

**Answer: D** - Every escape becomes a test case for the reviewer.

</details>

### Q4. Where should review rules live so a PR can't weaken its own review?

- A. In the PR description
- B. In a comment
- C. In the PR's CLAUDE.md changes
- D. On the base branch: REVIEW.md for managed Code Review, or a checklist the CI reads from main

<details><summary>Answer</summary>

**Answer: D** - Managed Code Review reads REVIEW.md from the base branch for exactly this reason.

</details>
