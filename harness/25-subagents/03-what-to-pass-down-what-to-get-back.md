---
type: lesson
title: "What to pass down, what to get back"
minutes: 7
---

The handoff is where subagent designs succeed or fail. The subagent knows **only** what you put in its first message. The parent learns **only** what comes back.

## Passing down: a brief, not a hint

The parent model writes the `task` - and models write short tasks. "Restart search." is a complete thought to the parent, which has the whole conversation. To the subagent it's missing everything: which cluster, what not to touch, why.

A good brief has:

| Part | Example |
|---|---|
| **The goal** | Find which log has the slowest request |
| **Inputs** | logs/part1.log, part2.log, part3.log |
| **Constraints** | Read only; don't open other files |
| **What to return** | The file name and the slowest time, plus the files you used |
| **Context the parent has** | The user's original request, pinned facts (topic 18) |

Two ways to get it: describe it in the `delegate` tool description so the model writes better tasks, and have the **harness** add the parts it knows for sure - the original request and pinned constraints. Topic 28 shows what happens when you don't.

## Getting back: a report, not a transcript

| Return | Why |
|---|---|
| The answer | What the parent asked for |
| Evidence pointers | "from logs/part2.log line 41" - so the parent (or a verifier) can check |
| What it did | Actions with side effects, so the parent doesn't repeat them |
| What it couldn't do | "part3.log was missing" - instead of silently guessing |

Cap the size (1,500 characters is plenty), and say in the subagent's system prompt what the report must contain.

## Don't share what isn't needed

- **Tools:** give the subagent only the tools its job needs. A research subagent doesn't need `send_email`.
- **No recursion by default:** a subagent that can delegate can spawn subagents forever.
- **Budgets:** its own step limit and token budget, counted toward the parent's total (topic 32).
