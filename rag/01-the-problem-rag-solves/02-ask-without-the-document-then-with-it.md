---
type: lesson
title: "Ask without the document, then with it"
minutes: 8
---

Time to see the problem and the fix with your own eyes. This VM has the `claude` command ready. Ask it something only your team could know:

```bash
claude -p "What time does the payments team deploy to production?"
```

```text
I don't have any information about the payments team's deployment
schedule. This isn't something in my memory or current context.

Could you point me to where this might be documented - e.g., a
wiki page, a README, or a team handbook?
```

An honest reply, and a dead end. The model does not know your team, says so, and asks you for a document. Your exact wording will differ between runs and models - some replies list general advice about how teams usually deploy - but none of them can contain your real deploy time. It was never in the model.

## Now give it the document

The model asked for documentation. Give it some. Same question, with the runbook text in the prompt first:

```bash
claude -p "Answer the question using only the document below.

Document: The payments team deploys to production every Tuesday
at 15:00 UTC. Deploys are frozen in the last week of December.

Question: What time does the payments team deploy to production?"
```

```text
The payments team deploys to production every Tuesday at 15:00 UTC.
```

Same model. Same question. Completely different result: short, exact, and correct. Nothing about the model changed. The only change is that the answer was in the prompt this time.

## The one idea

This is the whole trick, and it is worth saying plainly: **a model answers well when the facts it needs are inside the prompt.** The rest of this course is about doing this move well - finding the right document, cutting it to the right piece, and putting that piece in the prompt automatically.

In the next task you do both runs yourself with your own document.
