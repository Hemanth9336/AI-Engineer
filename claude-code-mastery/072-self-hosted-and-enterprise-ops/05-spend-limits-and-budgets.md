---
type: lesson
title: "Spend limits and budgets"
minutes: 10
---

Spend control works in layers. Each one bounds a different blast radius:

| Layer | Bounds | Mechanism |
|---|---|---|
| **Per run** | One agent run | `--max-budget-usd`, `--max-turns`, `max_budget_usd` in the SDK |
| **Per job** | A CI job or cron flow | The wrapper sums `total_cost_usd` from envelopes and alerts (topics 066-067) |
| **Per developer** | One person's day, week or month | Gateway spend limits; subscription usage limits on seats |
| **Per group / organization** | A team or the whole company | Gateway group and org caps; Console workspace spend limits; cloud budgets and alerts in AWS or GCP |
| **Per provider account** | The bill | Cloud budgets, quotas, and your contract |

## Gateway spend limits

With the Claude apps gateway's admin API, caps are set per `user`, `rbac_group` or `organization`, and per `daily`, `weekly` or `monthly` period, in USD cents:

```bash
curl -sS https://claude-gateway.internal.example.com/v1/organizations/spend_limits \
  -H "x-api-key: $GATEWAY_ADMIN_WRITE_KEY" -H "Content-Type: application/json" \
  -d '{"scope": {"type": "rbac_group", "rbac_group_id": "contractors"}, "amount": "10000", "period": "daily"}'
```

- A group or org cap is a **per-person default**, not a shared pool. Each developer's effective cap is their own override if one exists, otherwise their most restrictive group cap, otherwise the org default.
- Over the cap, the next request gets `429` (`billing_error`, `x-should-retry: false`) with the reset time. Claude Code warns at 75% and 95%, and `/usage` shows the bar.
- Costs are the gateway's **estimate** (list price, your overrides, or a conservative unknown-model rate). That makes it a circuit breaker, not an invoice. Reconcile with the provider's bill.
- If the gateway's Postgres is unreachable, enforcement **fails open** by default, so a database outage doesn't become an inference outage. Set `enforcement.fail_closed_on_error: true` when no unmetered spend is acceptable.
- Give each automation its own admin key, so the audit log shows who changed which cap.

## Budgets that help rather than block

1. Start from data. Take the 90th-percentile daily spend per developer from your telemetry, then set caps a comfortable margin above it.
2. Alert before you block. Telemetry alerts at 50% of the monthly budget reach the team lead before any cap reaches the developer.
3. Treat automation differently. A bot account in its own group, with its own cap, keeps a runaway CI loop from eating anyone's personal allowance, and makes the runaway obvious.
4. Review monthly. Look at top spenders by flow and by person, and at blocked requests that were legitimate work.

## Commands this node introduces

`/v1/organizations/spend_limits`, `scope` (`user`, `rbac_group`, `organization`), `period`, `amount` in cents, `429 billing_error`, `enforcement.fail_closed_on_error`, and layered budgets.
