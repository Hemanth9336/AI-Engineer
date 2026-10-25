---
type: lesson
title: "When parallelism hurts"
minutes: 7
---

Parallel subagents feel like free speed. They aren't free, and sometimes they aren't even speed.

## The costs

| Cost | What happens |
|---|---|
| **Tokens** | Each subagent pays its own system prompt and tool definitions. Five subagents = five copies |
| **Rate limits** | 10 concurrent agents x 5 steps = 50 calls in a burst. Providers answer with 429s, and retries add delay (topic 9) |
| **Merging** | Five reports written in five styles, sometimes contradicting each other. Someone - the parent model - has to reconcile them, and that costs another call |
| **Debugging** | Interleaved logs from five loops. Without a run ID per subagent, traces are unreadable (topic 31) |

## When the work isn't independent

Parallelism only helps when tasks really don't depend on each other.

- **Shared state:** two subagents editing the same file overwrite each other. Two "fix the bug" agents each make a different fix.
- **Order matters:** "find the failing service, then read its logs" is a sequence. Running both at once means the second guesses.
- **Duplicated work:** three subagents each list the same directory and read the same README, because nobody told them the others exist.

Rule of thumb: parallelize **reading** freely, **writing** rarely, and **deciding** never - one agent makes the decision from the merged reports.

## Limits to set

- **`max_workers`** - a concurrency cap that fits your rate limits (3-5 is typical for one user's task).
- **A timeout per subagent** - one stuck subagent shouldn't hold the whole fan-in.
- **A total budget** - the sum of all subagents' tokens counts against the task (topic 32).
- **Partition writes** - if subagents must write, give each its own output file or directory.

## Measure before you parallelize

Time the sequential version and count its tokens. If the subtasks take 2 seconds each, parallelism saves 4 seconds and costs extra system prompts and a merge call. If they take 90 seconds each, it's an easy win.
