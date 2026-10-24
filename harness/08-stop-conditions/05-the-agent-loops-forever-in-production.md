---
type: scenario
title: "The agent loops forever in production"
minutes: 3
---

**Situation.** Stackline's on-call assistant investigates alerts: it reads logs, checks service configs and posts a summary. On Saturday it ran a single investigation for 3 hours and 41 minutes - 2,212 model calls - before someone noticed the bill. The trace shows the same pattern from step 9 onwards:

```text
step  9  search_logs(service="search", query="timeout")  -> "error: log store unavailable (503)"
step 10  search_logs(service="search", query="timeout")  -> "error: log store unavailable (503)"
step 11  search_logs(service="search", query="timeout")  -> "error: log store unavailable (503)"
...
```

The harness is a `while True:` loop. The team's first suggestion is to add "Do not repeat the same tool call" to the system prompt.

### Q1. What is the most important fix to ship first?

- A. Add the sentence to the system prompt
- B. Switch to a larger model
- C. A hard step limit in the harness, so no investigation can exceed a set number of calls
- D. Increase the log store's capacity

<details><summary>Answer</summary>

**Answer: C** - The prompt is a request. A step limit is a guarantee - it bounds every future runaway, whatever the cause.

</details>

### Q2. Traces of successful investigations show 95% finish within 14 steps. Which limit is sensible?

- A. 5
- B. 20-30
- C. 2,000
- D. No limit, but alert after an hour

<details><summary>Answer</summary>

**Answer: B** - Above the normal range so good runs aren't cut off, far below the disaster. 5 would break normal runs; 2,000 is the incident.

</details>

### Q3. Which extra guard would have stopped this exact pattern at step 11?

- A. A longer system prompt
- B. Repeat detection: the same call with the same arguments three times in a row stops the run (or tells the model)
- C. Raising max_tokens
- D. Lower temperature

<details><summary>Answer</summary>

**Answer: B** - Identical call, identical error, three times: a cheap check catches it long before any step limit.

</details>

### Q4. The tool returned 'error: log store unavailable (503)'. How could the result itself help the model stop?

- A. It can't - only the harness can stop a loop
- B. Say what to do next: 'error: log store unavailable (503). Don't retry - report that logs are unavailable.'
- C. Return an empty string instead
- D. Return the same error in capital letters

<details><summary>Answer</summary>

**Answer: B** - Error results are prompts too. Telling the model the error is persistent, and what to do instead, often ends the loop by itself - with the step limit as the backstop.

</details>

### Q5. After the limit is hit, what should the harness return?

- A. A clear 'stopped: reached max steps' result with a non-zero status, so callers and dashboards can count it
- B. Nothing - just exit
- C. Whatever the model last said
- D. A made-up summary

<details><summary>Answer</summary>

**Answer: A** - A limit hit is a failure you need to see and measure, not a silent success.

</details>
