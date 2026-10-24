---
type: lesson
title: "Wrapping a REST endpoint as a tool"
minutes: 5
---

Most customer systems expose a **REST API**: HTTP requests to URLs like `GET /v1/orders/MER-55120` that return JSON. Turning one into a tool is a thin wrapper - but the thin wrapper is where reliability lives.

## The wrapper

```python
import httpx

def get_order(order_id):
    try:
        r = httpx.get(f"{BASE}/v1/orders/{order_id}", timeout=5)
    except httpx.HTTPError:
        return {"error": "orders API unreachable"}
    if r.status_code == 404:
        return {"error": "order not found"}
    if r.status_code != 200:
        return {"error": f"orders API error {r.status_code}"}
    return r.json()
```

`httpx` is installed with the `openai` package, so you already have it.

## What the wrapper must handle

| Concern | Why |
|---|---|
| **Timeout** | Without one, a hung API hangs your assistant. 5-10 seconds is typical |
| **Status codes** | 404 is an answer ("no such order"), 500 is a failure, 401 is a credentials problem - tell them apart |
| **Errors as results** | Return `{"error": ...}`, never raise into the agent loop |
| **Trim the response** | Return the fields the model needs, not 200 fields of internal data |
| **Base URL from config** | `MERIDIAN_API_URL` from the environment - test, staging and production differ |
| **Validate inputs** | An order id that's 4,000 characters long or contains `../` shouldn't reach the API |

## Separate the client from the tool

Put the HTTP code in its own module (`orders_client.py`) and keep the tool definition and loop elsewhere. The client can then be tested on its own, reused by an MCP server or a batch job, and reviewed by the customer's API team without reading any AI code.

## Read the API docs - and then the real responses

Customer API docs are often out of date. Call the endpoint yourself with `curl` before writing the wrapper, look at real responses including errors, and note what's actually returned.

In the task, a mock version of Meridian's orders API is running on your machine at `127.0.0.1:4560`.
