---
type: lesson
title: "When to merge, split, or remove tools"
minutes: 6
---

Tool sets drift. Someone adds `get_user_v2`, someone else adds `quick_lookup`, and a year later the agent has 40 tools and picks the wrong one half the time. Treat the tool set as a design you review, with three moves.

## Merge: same job, different names

**Signal:** two tools could both answer the same question; traces show the model alternating between them.

```text
get_user(id) + fetch_user(email) + lookup_customer(name)  ->  find_customer(query)
get_invoices(user_id) + list_bills(customer)             ->  list_invoices(customer_id, status?)
```

Merge into one tool whose parameters cover the variants. One description, one name, no coin toss.

## Split: one tool, several jobs

**Signal:** a tool has a `mode` or `action` parameter that changes what it does, and the description is a paragraph of "if X then... if Y then...".

```text
manage_service(action="status" | "restart" | "scale" | "delete", ...)
  ->  get_service_status(service)        read-only
      restart_service(service)           write, needs approval
      scale_service(service, replicas)   write, needs approval
      (delete: removed from this agent)
```

Splitting is especially important when the jobs have **different risk**: you can't put an approval gate on "manage_service" without gating harmless status checks too (topic 15).

## Remove: not this agent's job

**Signal:** the tool is rarely called, or only ever called by mistake, or it belongs to a different workflow.

Removing a tool is the cheapest improvement there is: fewer tokens per step, fewer wrong picks, smaller attack surface.

## Load tools per task

If one product genuinely needs many tools, don't offer them all at once:

| Approach | How |
|---|---|
| **Per-agent sets** | A billing agent and a deploy agent, each with 5-8 tools |
| **Routing** | A first cheap call classifies the request, then the harness loads that category's tools |
| **Subagents** | The main agent delegates to a specialist that has the specialist tools (topic 25) |
| **Tool search** | One `find_tool(description)` tool that returns definitions on demand |

## How to decide

Look at traces, not at the list. Count, per tool: how often it's called, how often it's the wrong pick, how often its result is used. The data usually tells you which move to make.
