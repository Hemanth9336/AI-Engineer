---
type: lesson
title: "Token budgets"
minutes: 5
---

Caching and routing lower the average cost. **Budgets** cap the worst case. Without one, a runaway agent loop (topic 21), a script hammering the API, or a sudden traffic spike can turn a monthly bill into a weekly one - and the customer finds out from the invoice.

## Where to put limits

| Limit | Protects against |
|---|---|
| **max_tokens per call** | One answer rambling for 4,000 tokens |
| **Max steps per agent turn** | Tool loops that never end |
| **Per-user daily limit** | One user or bot scripting thousands of requests |
| **Per-application daily budget** | Total spend for the day, whatever the cause |
| **Provider-side spend limits and alerts** | Everything else - the last line of defence |

## Enforce in code, before the call

```python
if used_today() >= DAILY_TOKEN_LIMIT:
    raise BudgetExceeded(...)
resp = client.chat.completions.create(...)
record(resp.usage.total_tokens)
```

- **Check before** you call - once the request is sent, you've paid.
- **Record actual usage** from the response's `usage`, not an estimate.
- **Store it somewhere shared** - a file is fine for one process; production uses a database or Redis so every instance sees the same total.
- **Fail gracefully** - a clear message for users, an alert for the team.

## Set the number with the customer

Use the cost model from topic 4: expected requests x tokens per request, plus headroom (2-3x). Agree what happens at the limit: hard stop, switch to a cheaper model, or alert only. A hard stop protects the budget; a soft limit protects the service. It's a business decision - make it explicitly.
