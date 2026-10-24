---
type: lesson
title: "Human-in-the-loop and feedback signals"
minutes: 6
---

Even a good assistant needs a way to hand over to people - and a way for people to tell you when it got something wrong.

## Feedback signals

| Signal | Cost to the user | What it tells you |
|---|---|---|
| **Thumbs up / down** | One click | Which answers failed - the cheapest, highest-volume signal |
| **Free-text comment** on thumbs-down | A few seconds | *Why* it failed |
| **Edits to a draft** before sending | None - captured automatically | How far the draft was from acceptable |
| **Escalation / "talk to a person"** | One click | Where the assistant can't help |
| **Follow-up question** ("no, I meant...") | None | The first answer missed |

Store each signal with the **request id** (topic 35), so a thumbs-down links straight to the question, retrieval and answer.

## When to hand over to a human

Escalation rules decide when the assistant should stop and route to a person, instead of trying again:

- The assistant **refused** - it doesn't have the answer.
- The user **asks for a human** ("can I talk to someone?").
- The user is **angry** or mentions legal action - a person handles this better and the stakes are higher.
- **Repeated thumbs-down** in one session - the assistant isn't helping.
- **High-stakes actions** - refunds, account changes, anything irreversible (topic 20).

Start with simple, explainable rules. Measure how often each fires and what happens next.

## Humans as the safety net, not the crutch

Human review is essential in a pilot - but if agents rewrite 80% of drafts, the assistant isn't saving time. Track the edit rate and the escalation rate; both should fall as you fix the top failure buckets.
