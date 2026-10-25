---
type: quiz
title: "Quick check: the span that explains slow sessions"
minutes: 8
---

### Q1. Users say sessions feel slow. With traces on, which span covers one whole user turn?

- A. claude_code.llm_request
- B. claude_code.session.count
- C. claude_code.interaction
- D. api_request

<details><summary>Answer</summary>

**Answer: C** - The interaction span wraps the turn; its children show model time against tool time.

</details>

### Q2. Inside slow interactions, `claude_code.tool.blocked_on_user` spans are long. What does that mean?

- A. The model is slow
- B. Time was spent waiting for a human permission decision, not on compute
- C. Network latency
- D. A bug

<details><summary>Answer</summary>

**Answer: B** - Permission prompts can dominate wall time; allow rules for safe commands remove them.

</details>

### Q3. You set every exporter but nothing arrives. Which variable did you probably forget?

- A. OTEL_EXPORTER_OTLP_HEADERS
- B. OTEL_LOG_USER_PROMPTS
- C. OTEL_RESOURCE_ATTRIBUTES
- D. CLAUDE_CODE_ENABLE_TELEMETRY=1

<details><summary>Answer</summary>

**Answer: D** - It's the master switch; without it nothing is exported.

</details>

### Q4. Which metric would you chart for spend per team?

- A. claude_code.session.count
- B. claude_code.cost.usage, grouped by your team resource attribute
- C. claude_code.active_time.total
- D. claude_code.commit.count

<details><summary>Answer</summary>

**Answer: B** - cost.usage carries model; your resource attributes carry the team.

</details>

### Q5. A short `claude -p` run exits and the collector shows no metrics. Most likely?

- A. Telemetry only works interactively
- B. OTLP needs grpc
- C. The export interval is longer than the run and the collector was stopped before the final flush arrived
- D. Metrics are sampled

<details><summary>Answer</summary>

**Answer: C** - Lower the intervals for tests and give the exporter a moment after exit.

</details>
