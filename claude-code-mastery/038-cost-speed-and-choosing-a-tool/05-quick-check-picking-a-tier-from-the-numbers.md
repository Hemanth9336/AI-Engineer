---
type: quiz
title: "Quick check: picking a tier from the numbers"
minutes: 5
---

### Q1. Haiku: 3/5 passed, total $0.06. Sonnet: 5/5 passed, total $0.20. Your rubric's quality floor is 100%. What do the numbers say?

- A. Haiku is cheaper per success, and the floor picks haiku
- B. Sonnet is cheaper per success, and the floor picks sonnet
- C. Haiku is cheaper per success ($0.02 vs $0.04), but the floor picks sonnet
- D. They cost the same per success; pick by latency

<details><summary>Answer</summary>

**Answer: C** - Haiku: $0.06 / 3 = $0.02 per success; sonnet: $0.20 / 5 = $0.04. Haiku's 60% pass rate misses the floor, so only sonnet is eligible.

</details>

### Q2. Why report the median of three runs instead of the first run?

- A. The first run is always cached
- B. JSON reports only medians
- C. The median is always lower
- D. Runs vary in turns and latency; one run is an anecdote

<details><summary>Answer</summary>

**Answer: D** - Models aren't deterministic and latency varies; the median resists one outlier.

</details>

### Q3. A run's `modelUsage` lists two models although you passed `--model sonnet`. Most likely?

- A. The flag was ignored
- B. The JSON is corrupt
- C. Claude Code used a smaller model for background work in the same run
- D. You were billed twice

<details><summary>Answer</summary>

**Answer: C** - modelUsage breaks spend down per model, including small background calls.

</details>

### Q4. Your budget dashboard says one run cost $0.31, but you are on a Max subscription. What is that number?

- A. The amount charged to your card
- B. A bug
- C. A local estimate at list price; subscription usage isn't billed per run
- D. The cost of caching only

<details><summary>Answer</summary>

**Answer: C** - total_cost_usd is computed locally from token counts at list price.

</details>
