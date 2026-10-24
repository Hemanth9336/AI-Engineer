---
type: lesson
title: "Retries and backoff"
minutes: 6
---

Some errors are the model's fault: a wrong name, a value out of range. Retrying them unchanged gives the same error. Others are **transient**: a timeout, a dropped connection, a 503 from an overloaded service. Those often succeed a second later. A good harness tells them apart.

## Retry only what can succeed next time

| Retry | Don't retry |
|---|---|
| `TimeoutError`, `ConnectionError` | `KeyError`, `ValueError`, `TypeError` |
| HTTP 429 (rate limited), 500, 502, 503, 504 | HTTP 400, 401, 403, 404 |
| "service temporarily unavailable" | "invalid argument", "permission denied" |

Retrying a permanent error just triples the latency and the log noise. Send it straight back to the model.

## Back off between attempts

Hammering a struggling service makes it worse. Wait longer after each failure - **exponential backoff**:

```python
import time

RETRYABLE = (TimeoutError, ConnectionError)


def with_retries(fn, *args, attempts=3, base_delay=0.5, **kwargs):
    for i in range(attempts):
        try:
            return fn(*args, **kwargs)
        except RETRYABLE:
            if i == attempts - 1:
                raise                         # out of attempts: let run_tool report it
            time.sleep(base_delay * 2 ** i)   # 0.5s, then 1s, then 2s...
```

Production code usually adds **jitter** (a small random amount) so that a thousand agents don't all retry at the same instant.

## Two layers of retries

| Layer | What fails | Who retries |
|---|---|---|
| The model call | the provider returns 429 or 503 | The OpenAI SDK retries twice by default (`max_retries`) |
| A tool call | your service times out | **Your** harness, with code like the above |

After the last attempt, the error still goes to the model as text - `error: TimeoutError: status API timed out after 2s`. Then the model can decide: try a different tool, or tell the user the status API is down.

## Retries multiply cost and time

Three attempts with backoff can add several seconds to a step. Cap the attempts, and count retries in your trace - a tool that needs retries on every call is an incident waiting to happen, not a harness feature.
