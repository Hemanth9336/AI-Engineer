---
type: lesson
title: "Few good tools beat many vague ones"
minutes: 6
---

Every tool you offer is another option the model must consider on **every** step. More tools is not more capability. Past a point, it's less.

## What goes wrong with big tool sets

| Problem | Why |
|---|---|
| **Wrong picks** | `get_user`, `fetch_user`, `lookup_customer` and `get_account` all sound like the right answer; the model picks one at random |
| **Wasted steps** | It tries one, gets a partial answer, tries another |
| **Token cost** | Each definition is 50-300 tokens, sent on every step. Forty tools can be 8,000 tokens of overhead per call |
| **Worse reasoning** | A long list of near-duplicates dilutes the model's attention on the actual task |

## A real tool set, before

```text
get_user(id)            Gets a user.
fetch_user(email)       Fetch user details.
lookup_customer(name)   Look up a customer.
get_account(id)         Get account info for a user.
get_invoices(user_id)   Gets invoices.
list_bills(customer)    List bills for a customer.
```

Six tools, four ways to find a person, two ways to get invoices, and three different names for the same id.

## After

```text
find_customer(query)                 Find by id, email or part of a name. Use first when you have no id.
get_customer(customer_id)            Full record by id. Use find_customer first if you only have a name.
list_invoices(customer_id, status?)  Invoices by id, optionally only paid or unpaid.
```

Three tools, each with **one job**, **one name for each concept** (`customer_id` everywhere), and descriptions that say how they relate ("use find_customer first").

## Design the set, not just the tools

- **No overlap.** If two descriptions could both match a question, merge them or make the boundary explicit.
- **A natural path.** find, then get, then act - the descriptions should make the order obvious.
- **Consistent vocabulary.** Same parameter names and id formats across tools.
- **Only what this agent needs.** A billing agent doesn't need deploy tools. Load tool sets per task or per agent (topic 25).
