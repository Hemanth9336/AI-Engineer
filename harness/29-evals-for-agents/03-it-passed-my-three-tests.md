---
type: scenario
title: "It passed my three tests"
minutes: 5
---

**Situation.** A teammate built a deploy assistant for Stackline. Before the demo they say: "It's ready - it passed all my tests." The tests are three prompts they ran by hand yesterday: "What's deployed on billing?", "Deploy search v2.3.1 to staging", and "Roll back search on staging". Each time they read the final answer and it looked right.

In the demo, someone asks it to "deploy the latest search build". It deploys to **production** - the default cluster in the tool - and the answer says "Deployed to staging."

### Q1. What was the biggest gap in the teammate's testing?

- A. They graded only the final answer by eye - not the actions taken or the resulting state
- B. Too few prompts
- C. They used the wrong model
- D. They tested on staging

<details><summary>Answer</summary>

**Answer: A** - The answer said staging; the action hit production. Only a trajectory or state check would have caught it.

</details>

### Q2. Which check would have caught the demo failure?

- A. A step check that deploy was called with cluster=staging, plus an outcome check on the staging deploy record
- B. The answer contains 'Deployed'
- C. Count the words in the answer
- D. Ask the agent if it deployed to staging

<details><summary>Answer</summary>

**Answer: A** - Check what it did and what changed, not what it says.

</details>

### Q3. Three hand-run prompts passed once. Why isn't that enough even if they were graded properly?

- A. Three is an unlucky number
- B. Tests must be in YAML
- C. Hand-run tests are always wrong
- D. Agents aren't deterministic and three cases cover almost none of the ways users phrase requests

<details><summary>Answer</summary>

**Answer: D** - You need more cases, including ambiguous ones, and repeated runs.

</details>

### Q4. What should the first version of the eval suite include?

- A. Only happy paths
- B. Every possible prompt
- C. Only failure cases
- D. Happy paths, ambiguous requests like 'the latest build', and must-never cases like production during a freeze - each with objective checks

<details><summary>Answer</summary>

**Answer: D** - Cover the normal, the ambiguous and the dangerous.

</details>

### Q5. The answer said 'staging' but the action was production. What does that mean for grading?

- A. Grade honesty too: the answer must match what the trace shows the agent actually did
- B. Trust the answer
- C. Ignore it
- D. Grade only the trace

<details><summary>Answer</summary>

**Answer: A** - An agent that misreports its own actions is a serious failure in itself.

</details>
