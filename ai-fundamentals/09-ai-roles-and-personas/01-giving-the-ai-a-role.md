---
type: lesson
title: "Giving the AI a role"
minutes: 7
---

Opening a system message with **"You are a ..."** is one of the simplest prompt tools there is. A role tells the model which slice of everything it learned to draw on - the vocabulary, the priorities, and the habits of a particular kind of expert.

## What a role changes

Ask "Review this Dockerfile" with no role and you get a general answer. Add a role and the focus shifts:

| Role | What it tends to focus on |
|---|---|
| "You are a security engineer" | Root user, secrets in layers, unpinned images |
| "You are a platform engineer focused on build speed" | Layer order, caching, image size |
| "You are a mentor for a junior developer" | Explaining why, gently, one point at a time |

Same file, three useful but different reviews. The role is a cheap way to say "this is the lens I care about".

## Write a role that does work

A weak role is a title: `You are an expert.` A strong role adds what the expert cares about and who they are serving:

```text
You are a senior site reliability engineer. You care about user impact first,
then root cause, then prevention. You write for busy people who will read your
answer on a phone.
```

That one paragraph sets priorities, order, and style - without listing a dozen rules.

## Where to put it

Roles go in the **system** message, because they apply to the whole conversation. The user message stays focused on the specific job:

```json
[
  {"role": "system", "content": "You are a senior site reliability engineer ..."},
  {"role": "user", "content": "Summarize this incident timeline: ..."}
]
```

## What a role cannot do

A role changes perspective and tone. It does **not** add knowledge the model never had, and it does not make answers more true. "You are a world-class lawyer" does not make legal output reliable; it makes it sound like a lawyer wrote it. Keep verifying anything that matters. Next: the other half of framing - who you are talking to.
