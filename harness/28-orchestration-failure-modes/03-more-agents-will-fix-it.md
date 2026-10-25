---
type: scenario
title: "More agents will fix it"
minutes: 5
---

**Situation.** Stackline's incident assistant is one agent with 14 tools. It's slow on big incidents and sometimes misses a log. An architect proposes a redesign: a planner agent, five specialist agents (logs, metrics, deploys, tickets, customers), a critic agent that reviews every specialist report, and a writer agent that drafts the summary - eight agents, talking through a shared message board.

In the prototype, incidents take 3x longer, cost 6x more, and on 2 of 10 test incidents the planner and the critic kept sending work back to each other until the step limit hit.

### Q1. What's the first question to ask before adding agents?

- A. Which model should each agent use?
- B. How many agents can we afford?
- C. What exactly fails today, and is it something a second context would fix?
- D. Which framework should we use?

<details><summary>Answer</summary>

**Answer: C** - Diagnose the failure first. 'Slow and misses a log' may be a tool-result or context-budget problem (topics 13, 17).

</details>

### Q2. Why did the planner and critic loop on 2 of 10 incidents?

- A. The models were too small
- B. A circular dependency with no owner for the final decision and no retry cap
- C. The message board was slow
- D. Too many tools

<details><summary>Answer</summary>

**Answer: B** - Ping-pong between agents needs a cap and one agent that decides.

</details>

### Q3. Where does 6x cost come from?

- A. Higher prices
- B. Network overhead
- C. Eight system prompts and tool sets, every report summarized and re-read by several agents, plus critic rounds
- D. Logging

<details><summary>Answer</summary>

**Answer: C** - Each agent and each handoff costs tokens; reviews multiply them.

</details>

### Q4. Which change is most likely to help the original problem?

- A. Add more specialist agents
- B. Replace all agents with one bigger prompt
- C. Keep one main agent, add one log-search subagent with a small report, and fix the log tool's results
- D. Add a second critic

<details><summary>Answer</summary>

**Answer: C** - Use a subagent where a fresh context clearly helps - big reading, small answer - and fix the tool.

</details>

### Q5. How do you decide between the designs?

- A. Ask the architect
- B. Choose the newer one
- C. Run both on the same incident eval suite and compare accuracy, cost, latency and failure rate
- D. Pick the one with fewer lines of code

<details><summary>Answer</summary>

**Answer: C** - Evals settle architecture debates (topics 29-33).

</details>
