---
type: lesson
title: "What to persist vs recompute"
minutes: 6
---

Writing everything to disk sounds safe, but stale memory is a bug factory: the agent "remembers" a port that changed last week, or resumes a task with a file listing from yesterday. Decide deliberately what to persist.

## Persist vs recompute

| Persist | Recompute (re-read or re-run) |
|---|---|
| The user's decisions and preferences | File contents - they change |
| The task and how far you got | Live status: health checks, metrics, queue sizes |
| Results that are expensive and stable (a 10-minute analysis) | Anything cheap to fetch again |
| What was already done that **must not** be repeated (an email sent, a ticket opened) | Directory listings, search results |

The question to ask: *if this is stale, what breaks?* A stale preference is mildly annoying. A stale "the deploy is done" is dangerous.

## Checkpoint and resume

Long tasks get interrupted: a step limit, a crash, a laptop lid, a rate-limit outage. A harness that can **resume** saves the work - and the cost - of starting over.

```text
step 1 -> save state.json
step 2 -> save state.json
step 3 -> ... killed / step limit
python agent.py --resume  -> load state.json, continue from step 3
finished -> delete state.json
```

The simplest checkpoint is the **message list itself**, saved after every step (after the tool results are appended, so the history is valid). Resuming is then just "load the messages and keep looping". Rules:

1. **Save after each complete step**, never halfway between a tool call and its result.
2. **Delete the checkpoint when the task finishes** - otherwise the next `--resume` resumes something that's done.
3. **Store the task with it**, so resume doesn't need the user to repeat the question.
4. **Make side effects idempotent**, or record them. If the crash happened right after "send email" but before the save, resume must not send it twice (a ticket ID or a `done:` record helps).
5. **Re-verify on resume** for anything time-sensitive: the agent may be resuming hours later.

## Notes vs state

Notes (the previous task) are small and live forever. State is big and lives for one task. Keep them in separate files, with separate rules.
