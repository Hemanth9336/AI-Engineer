---
type: scenario
title: "Scenario: the retyped checklist"
minutes: 9
---

Your team reviews every new API endpoint with a 9-point checklist. Each engineer pastes it into Claude from a wiki page, and the copies have drifted: some have 7 points, some say "auth" where others say "authorization and rate limits". Review results are impossible to compare.

### Q1. What is the first fix?

- A. Ask everyone to be more careful when pasting
- B. Commit the checklist as one prompt file (or project skill) with stable ids and a fixed output format
- C. Put the checklist in each engineer's ~/.claude/CLAUDE.md
- D. Switch everyone to opus

<details><summary>Answer</summary>

**Answer: B** - One versioned source removes the drift and makes results comparable.

</details>

### Q2. The team wants to type `/api-review` and have Claude also apply it when someone says "review this endpoint". What should it become?

- A. A prompt file
- B. A CLAUDE.md section
- C. A hook
- D. A project skill in .claude/skills/api-review/ with a description naming endpoint reviews

<details><summary>Answer</summary>

**Answer: D** - A skill is invokable by name and, through its description, by Claude when relevant.

</details>

### Q3. Why not paste the 9 points into the project CLAUDE.md?

- A. CLAUDE.md cannot hold lists
- B. It would load into every session, even ones that never review an endpoint
- C. CLAUDE.md is ignored in reviews
- D. It would override the model

<details><summary>Answer</summary>

**Answer: B** - CLAUDE.md costs context every session; a skill loads only when it is used.

</details>
