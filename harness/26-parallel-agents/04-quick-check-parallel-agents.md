---
type: quiz
title: "Quick check: parallel agents"
minutes: 5
---

### Q1. Why do threads work well for running subagents in Python?

- A. Subagents spend most of their time waiting on network calls
- B. Python threads run on several CPU cores
- C. Threads use less memory than processes
- D. The OpenAI SDK requires threads

<details><summary>Answer</summary>

**Answer: A** - While one thread waits for an HTTP reply, others can run.

</details>

### Q2. Why catch exceptions inside each subagent call instead of around pool.map?

- A. It's faster
- B. To hide errors
- C. map doesn't raise
- D. Otherwise one failure re-raises and you lose all the other results

<details><summary>Answer</summary>

**Answer: D** - Turn each failure into an error report and keep the rest.

</details>

### Q3. Three 2-second subagents take 6 seconds in your fan-out. What does that suggest?

- A. They're running one after another - something is serializing them
- B. The model is slow
- C. Parallelism works
- D. The network is down

<details><summary>Answer</summary>

**Answer: A** - Parallel runs should take about as long as the slowest one.

</details>

### Q4. Which work is safest to parallelize?

- A. Several agents editing the same file
- B. Deciding the final answer
- C. Steps where the second depends on the first
- D. Reading and summarizing independent files

<details><summary>Answer</summary>

**Answer: D** - Parallelize reading freely; writing rarely; deciding never.

</details>

### Q5. What limits should a fan-out have?

- A. None
- B. Only a total budget
- C. Only a concurrency cap
- D. A concurrency cap, a timeout per subagent and a total token budget

<details><summary>Answer</summary>

**Answer: D** - Rate limits, stuck subagents and runaway costs all need a limit.

</details>
