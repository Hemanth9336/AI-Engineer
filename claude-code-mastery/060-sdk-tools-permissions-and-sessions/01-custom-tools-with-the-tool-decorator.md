---
type: lesson
title: "Custom tools with the tool decorator"
minutes: 12
---

In topic 052 you wrote an MCP server as a separate process. The SDK can host one **inside your program**: decorate an async function with `@tool`, bundle the tools with `create_sdk_mcp_server`, and pass the result as an MCP server. There's no subprocess and no JSON-RPC to write. The tool runs in your process, with your database connections and your credentials.

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool("get_order", "Look up one order by id. Returns status and total.", {"order_id": str})
async def get_order(args):
    order = db.orders.get(args["order_id"])
    if order is None:
        return {"content": [{"type": "text", "text": f"No order {args['order_id']}"}], "is_error": True}
    return {"content": [{"type": "text", "text": json.dumps(order)}]}

shop = create_sdk_mcp_server(name="shop", version="1.0.0", tools=[get_order])
opts = ClaudeAgentOptions(mcp_servers={"shop": shop})
```

| Piece | Rule |
|---|---|
| Name | Claude sees `mcp__<server key>__<tool>`, here `mcp__shop__get_order`. That's the name for permission rules, hooks and `allowed_tools` |
| Description | The model chooses tools from it, so say what the tool returns and when to use it |
| Input schema | A `{"field": type}` dict for simple cases, or a full JSON Schema dict for enums, optional fields and nesting |
| Return value | `{"content": [blocks]}`. Add `"is_error": True` for a failure the model should read and correct, as with `isError` in topic 052 |
| Exceptions | An uncaught exception becomes a tool error too. Return a clear message instead, so the model knows what to change |

Custom tools are the right place for **narrow, typed capabilities**: `cancel_job(job_id)` instead of letting the agent run `psql` with full database credentials. Every capability you give as a tool, rather than as a shell, is one you can validate, log and limit.

## Commands this node introduces

`@tool`, `create_sdk_mcp_server`, `mcp_servers={...}`, and `mcp__<server>__<tool>` for in-process servers.
