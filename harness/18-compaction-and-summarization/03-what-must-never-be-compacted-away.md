---
type: lesson
title: "What must never be compacted away"
minutes: 6
---

A summary is lossy by design. The question is **what** it loses. Some things must survive every compaction exactly, and a summarizer model can't be trusted to keep them - it may paraphrase a ticket number, round a value, or decide a constraint "isn't important".

## Never summarize these

| Keep verbatim | Why |
|---|---|
| The system prompt | It's the rules. Summarized rules are weaker rules |
| The user's task | The goal. "Restart search" is not the same as "Restart search after 02:00, not before" |
| **User constraints and decisions** | "Don't touch billing", "use the Sunday window" - losing these causes the worst failures |
| **Exact identifiers and values** | Ticket IDs, versions, ports, paths - the agent will need them character for character |
| The most recent turns | The model is in the middle of using them |
| Unresolved errors | Otherwise the agent forgets the thing it was trying to fix |

## Pinning

The simplest reliable technique is to **pin** facts: keep them outside the summary, in a message the compactor carries forward untouched.

```text
[system prompt]
[task]
[pinned facts]                         <- never summarized, only merged
- Change window is Sunday 02:00-04:00 UTC (CHG-5521)
- Don't restart billing
[summary of earlier steps] ...         <- rewritten at every compaction
[last 2 turns]
```

Who pins?

- **The model**, with a `pin_fact` tool - you tell it in the tool description what deserves pinning.
- **The harness**, automatically - for example, every user message after the first one, or every error that hasn't been fixed yet.

## Structured summaries

A free-form summary drifts. A **structured** one is easier to check:

```text
Goal: ...
Done: read billing.yaml (port 8081), search.yaml (port 9200)
Found: search p99 jumped at 09:12
Open: which deploy caused it?
```

## Test it - don't hope

Compaction bugs are silent: the agent just gets a little worse on long tasks. The fix is a test with a **scripted model** (labmock): script the model to pin a fact, read enough to force compaction, use a **lossy** summarizer that drops everything, and then assert the fact is still in the last request. If the test also fails when pinning is removed, it really proves something.
