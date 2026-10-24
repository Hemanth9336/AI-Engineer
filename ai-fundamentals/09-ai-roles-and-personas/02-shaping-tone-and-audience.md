---
type: lesson
title: "Shaping tone and audience"
minutes: 7
---

A role says who is speaking. The **audience** says who is listening - and it changes an explanation even more than the role does.

## Same facts, different audience

The facts of an incident do not change, but what each reader needs does:

| Audience | What they need |
|---|---|
| On-call engineer | Exact error, affected service, the command that fixed it |
| Engineering manager | Impact, duration, root cause, follow-up actions |
| Finance director | How many customers were affected, for how long, whether money was lost, and whether it will happen again |
| Customers | What happened in plain words, that it is fixed, and an apology |

Tell the model which one it is writing for, and it will choose the right detail, vocabulary, and length on its own.

## Name the audience precisely

"Non-technical" helps. "A finance director who has never heard of Kubernetes and has two minutes" helps much more. Concrete audiences produce concrete choices.

## Tone is a separate dial

Tone is how it sounds: calm, apologetic, direct, upbeat. Name it, and give a comparison if you can:

```text
Tone: calm and factual, like a pilot announcing a short delay.
```

## Keep the facts fixed

Changing audience and tone should change the **wording**, not the **facts**. Two habits keep facts safe:

- Put the facts in the prompt yourself, clearly separated from the instructions.
- Say what must survive: "Keep the duration and the number of affected customers exactly as given."

```text
Rewrite the incident below for our finance director. Under 100 words, no technical
jargon. Keep the times, the duration, and the percentage of failed payments exactly
as written.
```

The model now knows what it may change (wording, order, detail) and what it may not (the numbers).

## Strip the jargon on purpose

Models love the vocabulary of whatever they are given. If the input says "pods were OOMKilled and p99 latency hit 9s", a casual "explain simply" may still echo those terms. Ask explicitly for no jargon, or list the words to translate ("say 'servers ran out of memory', not 'OOMKilled'"). Next, write one for a real incident.
