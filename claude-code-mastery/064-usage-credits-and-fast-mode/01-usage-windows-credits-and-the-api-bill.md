---
type: lesson
title: "Usage windows, credits, and the API bill"
minutes: 19
---

"Claude Code is expensive" or "Claude Code stopped working" usually turns out to be one of four different meters. Knowing which one you hit decides the fix.

## The four meters

| Meter | Who has it | What it limits | What you see when it runs out |
|---|---|---|---|
| **Subscription usage limits** | Pro, Max, Team and Enterprise seats signed in with a Claude account | Usage within a **rolling session window** (about five hours), plus **weekly** limits on top | A message that you've hit your limit, with the reset time. `/status` and `/usage` show where you stand |
| **Usage credits (extra usage)** | Subscription plans with it turned on | Lets you keep working past the plan's limit, billed at API rates up to a cap you set | Work continues, and the spend appears as extra usage on the account |
| **API billing** | Anyone authenticating with an API key (Console, or a cloud provider such as Bedrock or Vertex) | Your organization's spend limits and rate limits (requests and tokens per minute) | Rate-limit errors (`429`) or a spend-limit error, and `total_cost_usd` in every envelope |
| **Per-run caps** | Whatever you pass to the run | `--max-turns` and `--max-budget-usd` stop *one* run | `subtype: error_max_turns` or `error_max_budget_usd`, `is_error: true`, and a non-zero exit |

Subscription usage is shared across Claude surfaces. Chat in claude.ai, the desktop app and Claude Code all draw from the same allowance. An afternoon of heavy chat can leave less for the evening's coding session.

## Which one for which job

- **Interactive work by people:** subscription seats. Predictable per-seat cost, and the limits are generous for normal use.
- **Automation (CI, cron, the SDK):** an API key, or a cloud provider, with per-run caps and alerts on `total_cost_usd`. Don't run a team's CI on one person's subscription. It's against the intended use, it's shared with their own work, and it stops when they hit their window.
- **Burst capacity on a subscription:** usage credits with a sensible monthly cap, rather than upgrading every seat.

## Reading where you stand

```text
/status      account, model, and which auth method this session uses
/usage       plan usage against the current limits
/cost        this session's token usage and cost (API-key sessions)
```

From automation, the envelope is the meter. `total_cost_usd` and `modelUsage` on every run, summed per job, are what topic 066 builds on.

## Commands this node introduces

`/status`, `/usage`, `/cost`, `--max-budget-usd`, `error_max_budget_usd`, rolling usage windows, weekly limits, and usage credits.
