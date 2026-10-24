---
type: lesson
title: "The chat API shape: messages and roles"
minutes: 5
---

Nearly every model provider offers the same basic API, called **chat completions**. Learn it once and you can call OpenAI, Anthropic (through compatible gateways), open models, and your lab - with the same code.

## The request

You send an HTTP `POST` with a JSON body:

```json
{
  "model": "lab-mini",
  "messages": [
    {"role": "system", "content": "You are a support assistant for Meridian Logistics."},
    {"role": "user", "content": "Where is my parcel?"}
  ],
  "max_tokens": 200,
  "temperature": 0
}
```

- **`model`** - which model to use.
- **`messages`** - the conversation so far, as a list. Each message has a **role** and **content**.
- **`max_tokens`** - cap on output tokens (optional but wise).
- **`temperature`** - 0 for consistent answers, higher for variety.

## The three roles

| Role | Who writes it | Purpose |
|---|---|---|
| `system` | You, the developer | Instructions, rules, persona. The customer never sees it |
| `user` | The end user (or your code on their behalf) | The question or request |
| `assistant` | The model | Its earlier replies - you send them back to continue a conversation |

## The response

```json
{
  "model": "lab-mini",
  "choices": [
    {"index": 0, "message": {"role": "assistant", "content": "Could you share your tracking number?"}, "finish_reason": "stop"}
  ],
  "usage": {"prompt_tokens": 32, "completion_tokens": 9, "total_tokens": 41}
}
```

The reply text lives at `choices[0].message.content`. `finish_reason` tells you why it stopped: `stop` (it finished) or `length` (it hit `max_tokens` - the answer is cut off). `usage` is what you're billed.

## Authentication

Every request carries a key in a header: `Authorization: Bearer <key>`. In your lab the key is in `$LAB_AI_KEY` and the gateway is at `$LAB_AI_URL`. Never paste a key into a file you might share - read it from the environment.
