---
type: lesson
title: "From numbers to a decision rubric"
minutes: 9
---

Measurements only help if they turn into a rule people follow without re-running the experiment.

## Summarize per model

| Metric | Formula | Why |
|---|---|---|
| Success rate | passes / runs | Correctness comes first |
| Median wall time | median of `wall_s` | What a person waits |
| Median cost | median of `total_cost_usd` | The typical run |
| **Cost per success** | total cost / passes | The real price of one correct result; undefined (null) when nothing passed |

## Write the rubric

A good rubric fits on one page and answers "which tier do I use for *this* request?":

1. **Default tier per task class.** For example, "Lookups and data questions with an oracle: haiku. Multi-file changes: sonnet. Architecture and gnarly debugging: opus."
2. **Quality floor.** A tier is eligible only if its success rate on your measured task class is at or above a bar (say 100% of 3, or 90% of 10).
3. **Choose by cost per success, then latency.** Among eligible tiers, pick the lowest cost per success; break ties with median wall time.
4. **Escalation rule.** "If the run fails the check twice, re-run on the next tier up" - and log it, so the rubric gets revisited.
5. **Re-measure trigger.** New model versions, a new task class, or a month passing.

## Choosing a tool, not just a tier

The same discipline applies between Claude Code and Codex. Decide on what you can verify for **your** team: which tool's guardrail model fits your security requirements (rules on tool calls, or an OS sandbox), what already exists (CLAUDE.md, skills, hooks, MCP servers), how CI authenticates, and the measured cost per success on your own task - not a benchmark from a blog post.

## Commands this node introduces

`statistics.median`, cost per success, and a written escalation rule.
