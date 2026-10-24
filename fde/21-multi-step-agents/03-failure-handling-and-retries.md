---
type: lesson
title: "Failure handling and retries"
minutes: 5
---

Customer systems fail. APIs time out, databases lock, a depot service goes down for maintenance. An agent that crashes on the first exception is useless in production - and one that hides failures is dangerous.

## Two layers of handling

**1. In your code - retry transient failures.** Timeouts and connection errors often succeed on a second try:

```python
def run_tool(fn, args, retries=1):
    for attempt in range(retries + 1):
        try:
            return fn(**args)
        except Exception as e:
            last = e
    return {"error": f"{fn.__name__} unavailable: {last}"}
```

Keep retries small (one or two) with a short wait, and only for errors that might be temporary. Retrying "order not found" is pointless.

**2. In the model - recover gracefully.** When retries are exhausted, return the error **as the tool result**. The model can then:

- tell the user honestly what it couldn't check ("I couldn't reach the depot service, so I can't confirm the hours"),
- still give what it does know ("your order is at Rotterdam Waalhaven"),
- or try another route if one exists.

## What not to do

| Mistake | Result |
|---|---|
| Let the exception crash the agent | The user gets an error page |
| Return an empty result `{}` | The model may invent the missing data |
| Retry forever | Requests hang; costs climb; an outage gets worse |
| Swallow the error silently | Nobody knows the depot API is down |

## Make failures visible

Log every tool error with the tool name, arguments and exception. A spike in `depot_hours unavailable` in the logs is how you'll notice an outage before the customer's ops team calls you.

## Test it on purpose

Make failures happen in a test - an environment variable that makes the tool raise, or a fake function that fails once then succeeds. If you only test the happy path, the first real outage is your test.
