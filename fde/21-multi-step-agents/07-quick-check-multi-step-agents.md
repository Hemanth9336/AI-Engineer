---
type: quiz
title: "Quick check: multi-step agents"
minutes: 3
---

### Q1. Why must track_parcel return the depot id, not just 'held at the Rotterdam depot'?

- A. It's shorter
- B. JSON requires ids
- C. The next tool needs the id - returning it lets the model chain the calls reliably
- D. For logging only

<details><summary>Answer</summary>

**Answer: C** - Expose what the next step needs.

</details>

### Q2. depot_hours times out. What should the agent's code do?

- A. Crash
- B. Retry once or twice, then return an error result the model can explain
- C. Retry until it works
- D. Return {}

<details><summary>Answer</summary>

**Answer: B** - Bounded retries, then an honest error.

</details>

### Q3. Why is returning an empty {} after a failure risky?

- A. It's slow
- B. The model may invent the missing data
- C. It's invalid JSON
- D. It costs more

<details><summary>Answer</summary>

**Answer: B** - Absence looks like 'nothing to report' - say it failed.

</details>

### Q4. Which guard catches nearly every runaway loop?

- A. A maximum number of steps per turn
- B. Lower temperature
- C. A bigger model
- D. Shorter tool descriptions

<details><summary>Answer</summary>

**Answer: A** - Max steps is the essential first guard.

</details>
