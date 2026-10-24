---
type: lesson
title: "Blast radius thinking"
minutes: 7
---

Every permission decision is a bet on what happens when the model gets it wrong. **Blast radius** is the size of the damage in that worst case. Design permissions around it, not around how good the model is.

## Ask three questions per action

| Question | Small blast radius | Large blast radius |
|---|---|---|
| **Reversible?** | Write a file in a git repo | Delete a database table, send an email, pay an invoice |
| **How far does it reach?** | One file in the workspace | Every customer, every region, production |
| **Who notices, how fast?** | A failing test, in seconds | A customer, next month |

`rm build/cache.txt` and `DROP TABLE customers` are both "delete". They're not the same decision.

## Shrink the radius instead of adding approvals

Approval gates are the last line of defense, and people get tired of them. Better: make the dangerous version impossible.

| Instead of | Do |
|---|---|
| A prod DB connection with an approval prompt | A read-only replica user; writes go through a reviewed migration |
| `delete_file` on any path | A sandbox directory (topic 22); deletes go to a trash folder |
| An API key with admin scope | A key scoped to the 3 endpoints the agent uses, with a spend limit |
| "send_email to anyone" | Send to the user's own address, or drafts a human sends |
| Long-lived credentials | Short-lived tokens issued per task |

## Least privilege, per task

The same agent may need different powers for different jobs. A "summarize the incident" task needs read access to logs. A "roll back the deploy" task needs one write action, once. Grant per task, not per agent - and take it away when the task ends.

## Write it down

For each tool or command class, record in the repo: what it can touch, whether it's reversible, its decision (allow / ask / deny), and why. It's the document a security reviewer asks for first - and the one that makes the next "can we just auto-approve this?" discussion short.
