---
type: scenario
title: "The customer wants 40 tools exposed at once"
minutes: 4
---

**Situation.** Stackline is building an internal ops agent for its platform team. The team lead hands you a spreadsheet: 40 internal API endpoints - users, billing, deploys, feature flags, DNS, on-call schedules, log search, metrics, and a few admin endpoints like `purge_cache_all_regions` and `delete_tenant`. "Just expose all 40 as tools so the agent can do anything. The model is smart; it'll figure out which to use."

In a quick prototype with all 40, you measure: tool definitions alone are **9,400 tokens per call**, and on 30 test questions the agent picks a wrong tool first on 11.

### Q1. What's the strongest argument against exposing all 40 at once?

- A. Models can only use 10 tools
- B. It's against the API rules
- C. Accuracy and cost: 11 of 30 wrong first picks, and 9,400 tokens of definitions paid on every step
- D. The tools would be too slow

<details><summary>Answer</summary>

**Answer: C** - You have measurements. Lead with them: wrong picks waste steps, and the definition overhead multiplies with every call.

</details>

### Q2. Which design would you propose instead?

- A. Group tools into a few specialist agents or task-loaded sets, each with a handful of clear tools, behind a router
- B. Expose 40 tools but write longer descriptions
- C. Pick 40 random tools each day
- D. Let users choose tools manually for each question

<details><summary>Answer</summary>

**Answer: A** - Per-task tool sets keep each request small and unambiguous while the product as a whole can still reach all 40 endpoints.

</details>

### Q3. What should happen to purge_cache_all_regions and delete_tenant?

- A. Expose them like any other tool
- B. Rename them so the model doesn't notice them
- C. Leave them out of the general agent; if needed at all, put them behind a separate approval-gated flow
- D. Add 'be careful' to their descriptions

<details><summary>Answer</summary>

**Answer: C** - Irreversible, high-blast-radius actions don't belong in a general-purpose tool set (topics 15 and 21).

</details>

### Q4. The traces show users_get, users_fetch and users_lookup are each picked about a third of the time for the same questions. What do you do?

- A. Keep all three for flexibility
- B. Merge them into one find_user tool with parameters covering the variants
- C. Delete two at random
- D. Move them to the end of the list

<details><summary>Answer</summary>

**Answer: B** - Near-duplicates are coin tosses. Merge them.

</details>

### Q5. How do you show the team lead your proposal is better?

- A. Run the same 30 questions on both designs and compare first-pick accuracy, steps and tokens
- B. Explain that experts say fewer tools is better
- C. Show the shorter tool list
- D. Ask the model which design it prefers

<details><summary>Answer</summary>

**Answer: A** - The same experiment that found the problem proves the fix.

</details>
