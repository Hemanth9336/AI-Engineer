---
type: scenario
title: "The demo hallucinates in front of the exec"
minutes: 5
---

Live demo for Kestrel Bank's COO. She types: "What's our overdraft fee for business accounts?" The assistant replies confidently: "35 EUR per month." Her head of products frowns: "We don't charge a monthly overdraft fee." The room goes quiet.

### Q1. What do you say first?

- A. 'Good catch - this is exactly the kind of failure we test for. Let's look at what it retrieved' - then open the sources it used
- B. 'That's odd, it never does that'
- C. 'The model is being updated'
- D. Move on quickly to the next question

<details><summary>Answer</summary>

**Answer: A** - Own it, stay calm, investigate in front of them.

</details>

### Q2. The sources contain nothing about overdraft fees. What does that tell you?

- A. The model is broken
- B. The COO typed it wrong
- C. The documents are wrong
- D. It's a grounding failure: retrieval found nothing relevant, and the prompt or threshold didn't force a refusal - a known, fixable class of bug

<details><summary>Answer</summary>

**Answer: D** - Name the failure mode precisely.

</details>

### Q3. What do you commit to after the demo?

- A. Nothing
- B. A bigger model
- C. Add the question to the trap set, fix the refusal path (threshold and prompt), and send the before/after eval results within a few days
- D. Never demo live again

<details><summary>Answer</summary>

**Answer: C** - Turn the failure into a visible, measured fix.

</details>
