---
type: lesson
title: "Multi-turn conversations"
minutes: 7
---

A chat app feels like the model remembers you. It does not. Every request to an LLM API is **independent**: the model sees exactly the messages in that request, and nothing else.

## Memory is the messages list

To hold a conversation, the client sends the **whole history every time**:

```json
{"model": "lab-fast", "messages": [
  {"role": "system",    "content": "You are a helpful SRE."},
  {"role": "user",      "content": "Suggest a name for our payments on-call channel."},
  {"role": "assistant", "content": "#payments-oncall"},
  {"role": "user",      "content": "Write a one-line description for it."}
]}
```

The third message is the model's **previous reply**, copied back in by the client. Without it, "it" in the last message means nothing - the model never saw the name.

## The three roles

| Role | Who writes it | Purpose |
|---|---|---|
| `system` | You (the developer) | Standing instructions for the whole conversation |
| `user` | The person, or your program | Each new request |
| `assistant` | The model - copied back by you | Its earlier replies, so it stays consistent |

Messages alternate `user`, `assistant`, `user`, ... after the optional system message.

## Why this design matters to you

- **You control memory.** You can drop, summarize, or edit earlier turns - nothing is stored on the model side.
- **You pay for history.** Every turn re-sends everything before it, so turn 20 costs far more input tokens than turn 1.
- **You can fake history.** Putting a made-up assistant turn in the list is how few-shot examples work (topic 07): the model treats it as something it said.
- **Order matters.** The model reads top to bottom; the latest user message is what it answers.

## In code

A conversation loop is just a list that grows:

```bash
# after each reply, append it and the next question
jq --arg reply "$REPLY" --arg next "$NEXT" \
  '.messages += [{role: "assistant", content: $reply}, {role: "user", content: $next}]' \
  turn1.json > turn2.json
```

Next: what happens when that list gets too long.
