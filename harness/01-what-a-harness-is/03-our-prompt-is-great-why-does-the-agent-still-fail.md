---
type: quiz
title: "Our prompt is great, why does the agent still fail?"
minutes: 4
---

### Q1. A startup runs a support agent for a hosting company. The system prompt is 400 words, carefully written, and reviewed by the whole team. In production the agent still fails in three ways. It sometimes answers billing questions with plan prices from last year. It sometimes loops on the same lookup for minutes. And once it told a customer to delete a server. The team asks you what to do next.

- A. Add retries so that when the agent gives a bad answer, the harness asks it again
- B. Rewrite the prompt again, adding stronger warnings against each of the three failures
- C. Switch to a larger, more expensive model and keep everything else the same
- D. Fix the harness: give the agent a tool that reads current prices, add a step limit to the loop, and require approval before destructive actions

<details><summary>Answer</summary>

**Answer: D** - Each failure comes from the system around the model, not the wording. Old prices mean the model can't see current data - it needs a tool. Endless lookups mean the loop has no step limit. The delete advice needs a permission gate. Retries just repeat the same blind guess, a stronger prompt is still only a request, and a bigger model still can't see today's prices or stop itself.

</details>
