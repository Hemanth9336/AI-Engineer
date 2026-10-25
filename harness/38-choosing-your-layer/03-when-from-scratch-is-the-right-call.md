---
type: scenario
title: "When from scratch is the right call"
minutes: 5
---

A bank wants an agent inside its payments back office: it reads a flagged transaction, calls three internal risk services, and either clears it or opens a case. Constraints from the risk team: every model request and response must be stored for seven years in their audit system; at most two model calls per transaction; a fixed, small model running in their own cloud account; no third-party code that can execute shell commands may be installed on the servers; p95 latency under 3 seconds.

### Q1. Which layer fits best?

- A. Extend Claude Code
- B. A browser extension
- C. No agent at all, ever
- D. A small from-scratch loop (or a minimal SDK) on the raw API - the constraints are about the loop itself

<details><summary>Answer</summary>

**Answer: D** - A coding harness with shell tools is ruled out; strict per-call control is the requirement.

</details>

### Q2. Why is a general-purpose coding harness a poor fit here?

- A. It's too new
- B. It ships shell and file tools, its own prompts and loop behavior - hard to cap at two calls and audit token by token
- C. It can't call APIs
- D. It's too expensive

<details><summary>Answer</summary>

**Answer: B** - Its strengths (autonomy, many tools) are liabilities in this setting.

</details>

### Q3. Which course topics become the core of this build?

- A. Stop conditions and caps, tool design, verification, transcripts, cost/latency budgets and regression evals
- B. Only prompt wording
- C. Skills and hooks
- D. MCP servers

<details><summary>Answer</summary>

**Answer: A** - You own every layer, so every topic applies.

</details>

### Q4. The bank later wants engineers to debug the risk services from their terminals with an agent. Which layer for that?

- A. Extend an existing harness (Claude Code + an MCP server for the risk services), with read-only tools
- B. The same back-office harness
- C. Build a second one from scratch
- D. None

<details><summary>Answer</summary>

**Answer: A** - Different users, different task - the choice is per use case.

</details>
