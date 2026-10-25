---
type: quiz
title: "Quick check: where a run's cost lives"
minutes: 9
---

### Q1. Your SDK script needs the dollar cost of the run it just finished. Where is it?

- A. The last AssistantMessage
- B. ResultMessage.total_cost_usd
- C. SystemMessage.data
- D. It's only on the billing page

<details><summary>Answer</summary>

**Answer: B** - The final ResultMessage carries total_cost_usd together with usage, num_turns, and duration_ms.

</details>

### Q2. A run hits `max_turns`. What does your `async for` loop see?

- A. Nothing; the iterator just stops
- B. A ResultMessage with subtype error_max_turns, then a ResultError exception
- C. Only an exception, with no result
- D. A SystemMessage with the error

<details><summary>Answer</summary>

**Answer: B** - Save the result as it arrives; the exception follows it.

</details>

### Q3. Your script saves `result.json` after the `async for` loop. Runs that hit the budget cap leave no file. Why?

- A. The cap deletes files
- B. Files are written asynchronously
- C. Budget runs have no result
- D. ResultError propagated out of the loop before the save line ran

<details><summary>Answer</summary>

**Answer: D** - Catch ResultError (or write inside the loop) so failed runs are recorded too.

</details>

### Q4. Your SDK agent ignores the repo's `CLAUDE.md` and `.claude/settings.json` deny rules. What's missing?

- A. A newer SDK
- B. setting_sources=["project"] - by default the SDK loads no filesystem settings
- C. permission_mode="plan"
- D. An API key

<details><summary>Answer</summary>

**Answer: B** - The SDK starts isolated on purpose; opt in to the settings sources you want.

</details>

### Q5. Which field tells you whether cached prompt tokens were reused?

- A. num_turns
- B. duration_api_ms
- C. usage["cache_read_input_tokens"]
- D. session_id

<details><summary>Answer</summary>

**Answer: C** - Cache reads are billed far below fresh input; usage separates them.

</details>
