---
type: lesson
title: "Lost context, duplicated work, deadlocks"
minutes: 8
---

Multi-agent systems fail in ways a single loop can't, because information has to cross a **boundary** between contexts - and every crossing can drop something.

## The common failure modes

| Failure | What you see | Usual cause |
|---|---|---|
| **Lost context** | The subagent does the task, but wrong: wrong cluster, wrong customer, ignored constraint | The handoff carried the task, not the constraints. The parent model summarized "restart search on staging only, prod is frozen" as "Restart search." |
| **Duplicated work** | Three subagents each read the same README; a ticket is opened twice | Nobody told them what the others are doing or have done; reports don't mention side effects |
| **Conflicting work** | Two agents edit the same file; the second overwrites the first | Parallel writers to shared state (topic 26) |
| **Deadlock / ping-pong** | Agent A asks B for X, B asks A for X; or a reviewer and a writer bounce the same draft forever | Circular dependencies, no retry cap, no owner for the decision |
| **Telephone game** | Facts degrade through each layer: "about 300 errors" becomes "many errors" becomes "some errors" | Each hop summarizes the last summary |
| **Lost failures** | The subagent hit an error, reported "done", the parent believed it | Reports with no "what I couldn't do" section; no verification |

## Lost context is the most common - and the most dangerous

The parent model writes the subtask. It knows the constraint, so leaving it out seems harmless to it. The subagent can't know what it was never told, and it will happily restart **production** - with complete confidence.

You can't rely on the model to always write a perfect brief. Make the **harness** carry what must not be lost:

```python
def brief(task):
    return f"{task}\n\nOriginal user request (follow its constraints):\n{USER_REQUEST}"
```

- Always include the user's **original request** - verbatim, not paraphrased.
- Include **pinned facts** and constraints (topic 18).
- And enforce the important ones in the **tool** too: a `restart_service` that refuses production during a freeze can't be talked into it by any brief.

## Debugging orchestration

Log each subagent's full input (its first messages) and its report, with a run ID linking it to the parent step (topic 31). Lost-context bugs are obvious the moment you read what the subagent was actually given.
