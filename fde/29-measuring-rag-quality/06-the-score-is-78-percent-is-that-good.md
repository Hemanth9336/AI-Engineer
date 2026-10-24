---
type: scenario
title: "The score is 78 percent - is that good?"
minutes: 3
---

You present Meridian's first eval run: 78% correct on 100 golden questions, hit@3 of 0.95, faithfulness 99%, all 15 traps refused. The head of support frowns: "78%? That's a C-plus. Is this thing any good or not?"

### Q1. What do the numbers tell you about where the 22% of failures come from?

- A. Retrieval is broken
- B. Nothing - the number is all that matters
- C. The model is too small
- D. Retrieval and grounding look healthy - most failures are in generation or in the expected answers, so read them before concluding anything

<details><summary>Answer</summary>

**Answer: D** - High hit@3 and faithfulness point away from retrieval and invention.

</details>

### Q2. What's the best answer to 'is it any good?'

- A. 'Yes, 78% is industry standard'
- B. 'It depends'
- C. 'No, let's start over'
- D. Walk through the failures by bucket: for example 9 fixable with prompt changes, 8 where the docs contradict each other, 5 acceptable refusals - then the projected score after fixes

<details><summary>Answer</summary>

**Answer: D** - Failures by bucket turn a grade into a plan.

</details>

### Q3. She asks how this compares to her team. What should you have?

- A. Nothing - humans aren't measured
- B. A competitor's demo
- C. Benchmarks from the provider
- D. A baseline: the same questions answered by agents, or the team's known error and response-time figures

<details><summary>Answer</summary>

**Answer: D** - Without a baseline, 78% can't be judged.

</details>
